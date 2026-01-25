import cv2
import numpy as np
import json
import sqlite3
import threading
import time
import random
import math
import logging

# إعدادات التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- 1. محرك ذكاء اصطناعي محلي لتحليل الشاشة واكتشاف الأعداء ---

class ScreenAnalyzer:
    def __init__(self, target_color_lower, target_color_upper, sensitivity=0.8):
        """
        يقوم بتهيئة محلل الشاشة.

        Args:
            target_color_lower (tuple): الحد الأدنى للنطاق اللوني الهدف (HSV).
            target_color_upper (tuple): الحد الأعلى للنطاق اللوني الهدف (HSV).
            sensitivity (float): حساسية اكتشاف اللون.
        """
        self.target_color_lower = np.array(target_color_lower, np.uint8)
        self.target_color_upper = np.array(target_color_upper, np.uint8)
        self.sensitivity = sensitivity
        self.enemy_locations = []
        self.lock = threading.Lock()

    def process_frame(self, frame):
        """
        يعالج إطارًا واحدًا من الشاشة لاكتشاف الأعداء.

        Args:
            frame (np.array): إطار الشاشة (BGR).

        Returns:
            list: قائمة بإحداثيات مواقع الأعداء المكتشفين.
        """
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_frame, self.target_color_lower, self.target_color_upper)

        # تطبيق عمليات تمدد وتقلص لإزالة الضوضاء وتحسين الاكتشاف
        kernel_erode = np.ones((3, 3), np.uint8)
        kernel_dilate = np.ones((5, 5), np.uint8)
        mask = cv2.erode(mask, kernel_erode, iterations=1)
        mask = cv2.dilate(mask, kernel_dilate, iterations=2)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        current_locations = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            # تصفية الكفافات بناءً على المساحة (يمكن تعديلها)
            if area > 100 * self.sensitivity:
                x, y, w, h = cv2.boundingRect(cnt)
                center_x = x + w // 2
                center_y = y + h // 2
                current_locations.append((center_x, center_y))
                logging.debug(f"Enemy detected at: ({center_x}, {center_y}) with area {area}")

        with self.lock:
            self.enemy_locations = current_locations
        return self.enemy_locations

    def get_enemy_locations(self):
        """
        يسترجع قائمة بمواقع الأعداء المكتشفين حاليًا.

        Returns:
            list: قائمة بإحداثيات مواقع الأعداء.
        """
        with self.lock:
            return self.enemy_locations

# --- 2. منطق رياضي لعمل الـ Drag Headshot برمجياً ---

class DragHeadshotLogic:
    def __init__(self, screen_width, screen_height, sensitivity_multiplier=1.0):
        """
        يقوم بتهيئة منطق Drag Headshot.

        Args:
            screen_width (int): عرض الشاشة.
            screen_height (int): ارتفاع الشاشة.
            sensitivity_multiplier (float): مضاعف الحساسية للتحكم في سرعة السحب.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.sensitivity_multiplier = sensitivity_multiplier
        self.crosshair_center_x = screen_width // 2
        self.crosshair_center_y = screen_height // 2
        self.last_target_pos = None

    def calculate_drag_path(self, current_crosshair_pos, target_enemy_pos, frame_rate=60):
        """
        يحسب مسار السحب اللازم لاستهداف الرأس.

        Args:
            current_crosshair_pos (tuple): الموضع الحالي لمؤشر التصويب (x, y).
            target_enemy_pos (tuple): موضع العدو (x, y).
            frame_rate (int): معدل إطارات محاكاة الحركة.

        Returns:
            list: قائمة بالإحداثيات (x, y) التي يجب أن يمر بها مؤشر التصويب.
        """
        if not current_crosshair_pos or not target_enemy_pos:
            return []

        #تقدير موضع الرأس (يمكن تحسينه بذكاء اصطناعي أكثر تطورًا)
        # هنا نفترض أن الرأس يقع في الجزء العلوي من جسم العدو
        enemy_width = 50 # قيمة افتراضية لعرض جسم العدو
        head_offset_y = 0.2 # نسبة من ارتفاع العدو إلى الرأس

        # تقدير موضع الرأس (افتراضي)
        estimated_head_pos = (target_enemy_pos[0], target_enemy_pos[1] - enemy_width * head_offset_y)

        # حساب المسافة بين مؤشر التصويب والرأس
        dx = estimated_head_pos[0] - current_crosshair_pos[0]
        dy = estimated_head_pos[1] - current_crosshair_pos[1]

        # حساب عدد الخطوات اللازمة للحركة
        # يعتمد على المسافة الكلية والحساسية
        total_distance = math.sqrt(dx**2 + dy**2)
        steps = int(total_distance / (10 * self.sensitivity_multiplier)) # 10 قيمة افتراضية لخطوة واحدة
        if steps == 0:
            steps = 1

        path = []
        for i in range(steps + 1):
            progress = i / steps
            new_x = current_crosshair_pos[0] + dx * progress
            new_y = current_crosshair_pos[1] + dy * progress
            path.append((int(new_x), int(new_y)))

        return path

    def update_crosshair_pos(self, new_pos):
        """
        يحدث الموضع الحالي لمؤشر التصويب.

        Args:
            new_pos (tuple): الموضع الجديد لمؤشر التصويب (x, y).
        """
        self.crosshair_center_x, self.crosshair_center_y = new_pos

# --- 3. واجهة Kivy للدردشة النرجسية التي تعمل بقواعد بيانات محلية ---

# استيراد Kivy
try:
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.textinput import TextInput
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.gridlayout import GridLayout
    from kivy.properties import StringProperty, ListProperty
    from kivy.clock import Clock
    from kivy.lang import Builder
    KIVY_AVAILABLE = True
except ImportError:
    KIVY_AVAILABLE = False
    logging.warning("Kivy is not installed. The chat interface will be unavailable.")

if KIVY_AVAILABLE:
    KV = """
<ChatInterface>:
    orientation: 'vertical'
    padding: 10
    spacing: 10

    ScrollView:
        size_hint_y: 0.8
        do_scroll_y: True
        do_scroll_x: False
        GridLayout:
            id: chat_log
            cols: 1
            spacing: 5
            padding: 5
            size_hint_y: None
            height: self.minimum_height

    BoxLayout:
        size_hint_y: 0.1
        orientation: 'horizontal'
        padding: 5
        spacing: 5

        TextInput:
            id: message_input
            hint_text: 'Enter your narcissistic message...'
            multiline: False
            size_hint_x: 0.8

        Button:
            text: 'Send'
            size_hint_x: 0.2
            on_press: root.send_message()
"""
    Builder.load_string(KV)

    class ChatDatabase:
        def __init__(self, db_path='chat_history.db'):
            """
            يدير قاعدة بيانات الدردشة (SQLite).

            Args:
                db_path (str): مسار ملف قاعدة البيانات.
            """
            self.db_path = db_path
            self._create_table()

        def _create_table(self):
            conn = None
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sender TEXT NOT NULL,
                        message TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
            except sqlite3.Error as e:
                logging.error(f"Database error: {e}")
            finally:
                if conn:
                    conn.close()

        def add_message(self, sender, message):
            conn = None
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO messages (sender, message) VALUES (?, ?)", (sender, message))
                conn.commit()
            except sqlite3.Error as e:
                logging.error(f"Database error adding message: {e}")
            finally:
                if conn:
                    conn.close()

        def get_messages(self, limit=50):
            conn = None
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT sender, message, timestamp FROM messages ORDER BY timestamp DESC LIMIT ?", (limit,))
                return cursor.fetchall()[::-1] # عكس لترتيب الأقدم أولاً
            except sqlite3.Error as e:
                logging.error(f"Database error getting messages: {e}")
                return []
            finally:
                if conn:
                    conn.close()

    class ChatInterface(BoxLayout):
        messages = ListProperty([])

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.chat_db = ChatDatabase()
            self.load_initial_messages()
            self.bind(messages=self.update_chat_log)
            self.narcissistic_response_templates = [
                "Of course, you'd say that. It's a reflection of your impeccable taste.",
                "I completely agree. My words always resonate with brilliance.",
                "That's precisely what I expect from someone with such exceptional understanding.",
                "Indeed. It's rare to find someone who truly grasps my depth.",
                "Naturally. Your insight is merely confirming what I already know.",
                "You're finally seeing it! My genius is undeniable.",
                "A perfect observation. It mirrors my own flawless perspective.",
                "Yes, yes, of course. It's always about me, isn't it? And that's how it should be.",
                "Your appreciation is noted. It's a sign of your growing wisdom.",
                "What did you expect? My communication is always on a higher plane."
            ]
            self.sender_name = "The Supreme Intellect" # اسم المستخدم النرجسي

        def load_initial_messages(self):
            self.messages = [(sender, msg, ts) for sender, msg, ts in self.chat_db.get_messages()]

        def send_message(self):
            message_input = self.ids.message_input
            user_message = message_input.text.strip()

            if user_message:
                # إضافة رسالة المستخدم
                self.messages.append(("You", user_message, time.strftime("%Y-%m-%d %H:%M:%S")))
                self.chat_db.add_message("You", user_message)

                # توليد رد نرجسي
                response = random.choice(self.narcissistic_response_templates)
                self.messages.append((self.sender_name, response, time.strftime("%Y-%m-%d %H:%M:%S")))
                self.chat_db.add_message(self.sender_name, response)

                message_input.text = ""
                # تفعيل التحديث لتحديث الواجهة
                self.messages = list(self.messages)

        def update_chat_log(self, instance, value):
            chat_log = self.ids.chat_log
            chat_log.clear_widgets()
            for sender, message, timestamp in self.messages:
                lbl = Label(text=f"[{timestamp}] {sender}: {message}",
                            halign='left',
                            valign='top',
                            size_hint_y=None,
                            height=25) # ارتفاع كل سطر
                lbl.text_size = (chat_log.width - 10, None) # لضبط النص داخل حدود الخلية
                chat_log.add_widget(lbl)
            # تأكد من أن المؤشر في الأسفل بعد إضافة رسالة جديدة
            Clock.schedule_once(lambda dt: self.scroll_to_bottom(), 0.1)

        def scroll_to_bottom(self):
            scroll_view = self.parent.children[0] # افترض أن ScrollView هو العنصر الأول
            scroll_view.scroll_y = 0

    class ChatApp(App):
        def build(self):
            return ChatInterface()

# --- 4. محاكي التدريب (1 ضد 6) مدمج داخل كود بايثون ---

class TrainingSimulator:
    def __init__(self, screen_width, screen_height, num_targets=6, friendly_fire=False):
        """
        يقوم بتهيئة محاكي التدريب.

        Args:
            screen_width (int): عرض منطقة التدريب.
            screen_height (int): ارتفاع منطقة التدريب.
            num_targets (int): عدد الأهداف (الأعداء) لإنشائها.
            friendly_fire (bool): هل تمكين إطلاق النار على الأصدقاء (غير مستخدم حاليًا).
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.num_targets = num_targets
        self.friendly_fire = friendly_fire
        self.targets = []
        self.score = 0
        self.training_active = False
        self.lock = threading.Lock()
        self._initialize_targets()

    def _initialize_targets(self):
        with self.lock:
            self.targets = []
            for _ in range(self.num_targets):
                # تحديد موضع عشوائي للأهداف
                x = random.randint(int(self.screen_width * 0.2), int(self.screen_width * 0.8))
                y = random.randint(int(self.screen_height * 0.2), int(self.screen_height * 0.8))
                self.targets.append({'pos': (x, y), 'active': True, 'size': random.randint(20, 40)})

    def start_training(self):
        with self.lock:
            self._initialize_targets()
            self.score = 0
            self.training_active = True
            logging.info("Training session started.")

    def stop_training(self):
        with self.lock:
            self.training_active = False
            logging.info("Training session stopped.")

    def update_targets(self, frame_rate=60):
        """
        تحديث مواقع الأهداف بشكل عشوائي.

        Args:
            frame_rate (int): معدل تحديث محاكاة الحركة.
        """
        if not self.training_active:
            return

        with self.lock:
            for target in self.targets:
                if target['active']:
                    # حركة عشوائية بسيطة للأهداف
                    move_x = random.randint(-5, 5)
                    move_y = random.randint(-5, 5)
                    new_x = target['pos'][0] + move_x
                    new_y = target['pos'][1] + move_y

                    # التأكد من بقاء الأهداف ضمن حدود الشاشة
                    new_x = max(int(self.screen_width * 0.2), min(int(self.screen_width * 0.8), new_x))
                    new_y = max(int(self.screen_height * 0.2), min(int(self.screen_height * 0.8), new_y))
                    target['pos'] = (new_x, new_y)

    def is_hit(self, click_pos, hit_radius=15):
        """
        يتحقق مما إذا كان النقر يضرب أحد الأهداف.

        Args:
            click_pos (tuple): موضع النقر (x, y).
            hit_radius (int): نصف قطر منطقة الإصابة حول الهدف.

        Returns:
            bool: True إذا تم ضرب هدف، False بخلاف ذلك.
        """
        if not self.training_active:
            return False

        with self.lock:
            for target in self.targets:
                if target['active']:
                    dist = math.sqrt((click_pos[0] - target['pos'][0])**2 + (click_pos[1] - target['pos'][1])**2)
                    if dist < target['size'] / 2 + hit_radius:
                        target['active'] = False
                        self.score += 1
                        logging.info(f"Target hit! Score: {self.score}")
                        return True
            return False

    def get_target_locations(self):
        """
        يسترجع مواقع الأهداف النشطة.

        Returns:
            list: قائمة بإحداثيات مواقع الأهداف النشطة.
        """
        with self.lock:
            return [target['pos'] for target in self.targets if target['active']]

    def get_score(self):
        with self.lock:
            return self.score

    def get_active_target_count(self):
        with self.lock:
            return sum(1 for target in self.targets if target['active'])

# --- 5. نظام تحليل فيديو محلي ---

class VideoAnalyzer:
    def __init__(self, capture_source=0, output_dir="processed_videos"):
        """
        يقوم بتهيئة محلل الفيديو.

        Args:
            capture_source (int or str): مصدر التقاط الفيديو (0 للكاميرا الافتراضية، أو مسار ملف).
            output_dir (str): الدليل لحفظ الفيديوهات المعالجة.
        """
        self.capture_source = capture_source
        self.output_dir = output_dir
        self.video_capture = None
        self.is_capturing = False
        self.is_processing = False
        self.output_video_writer = None
        self.output_filename = None
        self.frame_width = 0
        self.frame_height = 0
        self.fps = 0
        self.processing_thread = None
        self.screen_analyzer = None # سيتم تهيئته لاحقًا عند بدء المعالجة
        self.drag_logic = None # سيتم تهيئته لاحقًا

        import os
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def set_screen_analyzer(self, analyzer: ScreenAnalyzer):
        """
        يضبط محلل الشاشة ليتم استخدامه أثناء تحليل الفيديو.
        """
        self.screen_analyzer = analyzer

    def set_drag_logic(self, logic: DragHeadshotLogic):
        """
        يضبط منطق Drag Headshot ليتم استخدامه أثناء تحليل الفيديو.
        """
        self.drag_logic = logic

    def start_capture(self, output_filename="output.avi"):
        """
        يبدأ التقاط الفيديو.

        Args:
            output_filename (str): اسم الملف لحفظ الفيديو المعالج.
        """
        if self.is_capturing:
            logging.warning("Capture is already in progress.")
            return

        self.video_capture = cv2.VideoCapture(self.capture_source)
        if not self.video_capture.isOpened():
            logging.error(f"Could not open video source: {self.capture_source}")
            return

        self.frame_width = int(self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = int(self.video_capture.get(cv2.CAP_PROP_FPS))
        if self.fps == 0: # قد لا يكون FPS متاحًا دائمًا
            self.fps = 30 # قيمة افتراضية

        self.output_filename = os.path.join(self.output_dir, output_filename)
        fourcc = cv2.VideoWriter_fourcc(*'XVID') # أو 'mp4v'
        self.output_video_writer = cv2.VideoWriter(self.output_filename, fourcc, self.fps, (self.frame_width, self.frame_height))

        self.is_capturing = True
        logging.info(f"Video capture started. Saving to {self.output_filename}")
        logging.info(f"Resolution: {self.frame_width}x{self.frame_height}, FPS: {self.fps}")

        # بدء معالجة الفيديو في خيط منفصل
        if not self.is_processing:
            self.is_processing = True
            self.processing_thread = threading.Thread(target=self._process_video)
            self.processing_thread.daemon = True
            self.processing_thread.start()

    def stop_capture(self):
        """
        يوقف التقاط الفيديو.
        """
        self.is_capturing = False
        if self.video_capture and self.video_capture.isOpened():
            self.video_capture.release()
            logging.info("Video capture stopped.")

        # إشارة إلى أن المعالجة يجب أن تتوقف
        if self.is_processing and self.processing_thread and self.processing_thread.is_alive():
            self.is_processing = False # إيقاف الحلقة الداخلية
            self.processing_thread.join(timeout=2) # الانتظار حتى ينتهي الخيط
            logging.info("Video processing stopped.")

        if self.output_video_writer:
            self.output_video_writer.release()
            self.output_video_writer = None

    def _process_video(self):
        """
        التابع الذي يتم تشغيله في خيط منفصل لمعالجة إطارات الفيديو.
        """
        logging.info("Video processing thread started.")
        while self.is_processing:
            if not self.is_capturing or not self.video_capture.isOpened():
                time.sleep(0.1)
                continue

            ret, frame = self.video_capture.read()
            if not ret:
                logging.warning("End of video stream or read error.")
                self.stop_capture() # إيقاف عند نهاية الفيديو
                break

            processed_frame = frame.copy()
            enemy_locations = []

            # 1. تحليل الشاشة واكتشاف الأعداء
            if self.screen_analyzer:
                enemy_locations = self.screen_analyzer.process_frame(frame)
                for x, y in enemy_locations:
                    cv2.circle(processed_frame, (x, y), 10, (0, 255, 0), -1) # رسم دوائر على الأعداء

            # 2. تطبيق منطق Drag Headshot (إذا كان هناك عدو ومؤشر تصويب)
            if self.drag_logic and enemy_locations:
                # الحصول على موقع مؤشر التصويب الحالي (يجب أن يتم تحديثه من واجهة المستخدم أو المحاكاة)
                # هنا نستخدم مركز الشاشة كمثال. في تطبيق حقيقي، ستأتي هذه القيمة من مكان آخر.
                current_crosshair_pos = (self.drag_logic.crosshair_center_x, self.drag_logic.crosshair_center_y)

                # اختيار أقرب عدو (أو أول عدو مكتشف)
                target_enemy_pos = min(enemy_locations, key=lambda pos: math.dist(current_crosshair_pos, pos))

                drag_path = self.drag_logic.calculate_drag_path(current_crosshair_pos, target_enemy_pos)
                if drag_path:
                    # رسم مسار السحب
                    for i in range(len(drag_path) - 1):
                        cv2.line(processed_frame, drag_path[i], drag_path[i+1], (0, 0, 255), 2)
                    # تحديث موضع مؤشر التصويب (محاكاة)
                    self.drag_logic.update_crosshair_pos(drag_path[-1])
                    cv2.circle(processed_frame, drag_path[-1], 5, (255, 0, 0), -1) # رسم مؤشر التصويب الجديد

            # 3. عرض معلومات على الإطار (اختياري)
            cv2.putText(processed_frame, f"Enemies: {len(enemy_locations)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # كتابة الإطار المعالج إلى ملف الفيديو
            if self.output_video_writer:
                self.output_video_writer.write(processed_frame)

            # عرض الإطار (اختياري، يعتمد على ما إذا كانت هناك واجهة رسومية)
            # cv2.imshow('Processed Video', processed_frame)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     self.stop_capture()
            #     break
        logging.info("Video processing thread finished.")

    def analyze_video_file(self, video_path, output_filename="processed_file.avi"):
        """
        يقوم بتحليل ملف فيديو موجود (بدون التقاط مباشر).

        Args:
            video_path (str): مسار ملف الفيديو المراد تحليله.
            output_filename (str): اسم الملف لحفظ الفيديو المعالج.
        """
        if self.is_processing:
            logging.warning("Analysis is already in progress.")
            return

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logging.error(f"Could not open video file: {video_path}")
            return

        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        if fps == 0:
            fps = 30

        output_path = os.path.join(self.output_dir, output_filename)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out_writer = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

        logging.info(f"Analyzing video file: {video_path}. Saving processed video to {output_path}")
        self.is_processing = True

        while self.is_processing:
            ret, frame = cap.read()
            if not ret:
                break

            processed_frame = frame.copy()
            enemy_locations = []

            if self.screen_analyzer:
                enemy_locations = self.screen_analyzer.process_frame(frame)
                for x, y in enemy_locations:
                    cv2.circle(processed_frame, (x, y), 10, (0, 255, 0), -1)

            if self.drag_logic and enemy_locations:
                # هنا، لا يوجد "مؤشر تصويب مباشر" من واجهة مستخدم، لذا قد نحتاج لافتراض مركز الشاشة
                # أو تمرير موضع محاكاة
                current_crosshair_pos = (frame_width // 2, frame_height // 2) # افتراضي
                target_enemy_pos = min(enemy_locations, key=lambda pos: math.dist(current_crosshair_pos, pos))

                drag_path = self.drag_logic.calculate_drag_path(current_crosshair_pos, target_enemy_pos)
                if drag_path:
                    for i in range(len(drag_path) - 1):
                        cv2.line(processed_frame, drag_path[i], drag_path[i+1], (0, 0, 255), 2)
                    # لا نقوم بتحديث drag_logic.crosshair_center_x هنا لأننا لا نتحكم في واجهة حقيقية

            cv2.putText(processed_frame, f"Enemies: {len(enemy_locations)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            out_writer.write(processed_frame)

        cap.release()
        out_writer.release()
        self.is_processing = False
        logging.info(f"Video file analysis complete. Processed video saved to {output_path}")

# --- الوظيفة الرئيسية لتشغيل المكونات ---

class CoreLogic:
    def __init__(self, screen_width=1920, screen_height=1080, enemy_color_lower=(0, 150, 100), enemy_color_upper=(50, 255, 255)):
        """
        يقوم بتهيئة المكونات الأساسية للذكاء السيادي.

        Args:
            screen_width (int): عرض الشاشة الافتراضي.
            screen_height (int): ارتفاع الشاشة الافتراضي.
            enemy_color_lower (tuple): النطاق اللوني السفلي لاكتشاف الأعداء (HSV).
            enemy_color_upper (tuple): النطاق اللوني العلوي لاكتشاف الأعداء (HSV).
        """
        self.screen_width = screen_width
        self.screen_height = screen_height

        # 1. إعداد محلل الشاشة
        self.screen_analyzer = ScreenAnalyzer(target_color_lower=enemy_color_lower, target_color_upper=enemy_color_upper)

        # 2. إعداد منطق Drag Headshot
        self.drag_headshot_logic = DragHeadshotLogic(screen_width=self.screen_width, screen_height=self.screen_height)

        # 3. إعداد واجهة الدردشة (إذا كانت Kivy متاحة)
        self.chat_app = None
        if KIVY_AVAILABLE:
            self.chat_app = ChatApp()
            self.chat_thread = threading.Thread(target=self.chat_app.run)
            self.chat_thread.daemon = True
            self.chat_thread.start()
            logging.info("Chat interface starting in a separate thread.")

        # 4. إعداد محاكي التدريب
        self.training_simulator = TrainingSimulator(screen_width=self.screen_width, screen_height=self.screen_height)

        # 5. إعداد محلل الفيديو
        self.video_analyzer = VideoAnalyzer(capture_source=0) # 0 للكاميرا الافتراضية

        # ربط المكونات ببعضها البعض
        self.video_analyzer.set_screen_analyzer(self.screen_analyzer)
        self.video_analyzer.set_drag_logic(self.drag_headshot_logic)

        self.running = False
        self.main_loop_thread = None

    def _main_loop(self):
        """
        الحلقة الرئيسية التي تنسق عمل المكونات.
        """
        logging.info("Core logic main loop started.")
        while self.running:
            # تحديث محاكي التدريب
            self.training_simulator.update_targets()

            # تحديث مواقع الأعداء المكتشفين (إذا كان هناك التقاط للشاشة)
            # هذا يعتمد على أن ScreenAnalyzer يتم تحديثه بواسطة VideoAnalyzer.
            # إذا كان هناك استخدام منفصل لالتقاط الشاشة، نحتاج إلى آلية أخرى.
            if self.video_analyzer.is_capturing or self.video_analyzer.is_processing:
                # يتم تحديث enemy_locations داخل ScreenAnalyzer.process_frame
                pass

            # تحديث مؤشر التصويب (في حالة التدريب أو المحاكاة)
            if self.training_simulator.training_active:
                target_locations = self.training_simulator.get_target_locations()
                if target_locations:
                    current_crosshair_pos = (self.drag_headshot_logic.crosshair_center_x, self.drag_headshot_logic.crosshair_center_y)
                    # البحث عن أقرب هدف تدريبي
                    target_enemy_pos = min(target_locations, key=lambda pos: math.dist(current_crosshair_pos, pos))
                    drag_path = self.drag_headshot_logic.calculate_drag_path(current_crosshair_pos, target_enemy_pos)
                    if drag_path:
                        self.drag_headshot_logic.update_crosshair_pos(drag_path[-1])

            time.sleep(1 / 60) # محاكاة معدل إطارات (يمكن تعديله)
        logging.info("Core logic main loop stopped.")

    def start(self):
        """
        يبدأ تشغيل النظام.
        """
        if self.running:
            logging.warning("System is already running.")
            return

        self.running = True
        self.main_loop_thread = threading.Thread(target=self._main_loop)
        self.main_loop_thread.daemon = True
        self.main_loop_thread.start()
        logging.info("CoreLogic system started.")

    def stop(self):
        """
        يوقف تشغيل النظام.
        """
        if not self.running:
            logging.warning("System is not running.")
            return

        self.running = False
        self.video_analyzer.stop_capture()
        if self.main_loop_thread and self.main_loop_thread.is_alive():
            self.main_loop_thread.join(timeout=2)
        logging.info("CoreLogic system stopped.")

    def start_training_session(self):
        self.training_simulator.start_training()

    def stop_training_session(self):
        self.training_simulator.stop_training()

    def start_video_capture(self, filename="capture.avi"):
        self.video_analyzer.start_capture(output_filename=filename)

    def stop_video_capture(self):
        self.video_analyzer.stop_capture()

    def analyze_video_file(self, video_path, output_filename="processed_video.avi"):
        self.video_analyzer.analyze_video_file(video_path, output_filename)

    def simulate_click(self, click_pos):
        """
        محاكاة نقرة الماوس.
        """
        if self.training_simulator.training_active:
            self.training_simulator.is_hit(click_pos)
        # هنا يمكن إضافة منطق إطلاق النار على الأعداء المكتشفين في وضع اللعب الحقيقي

    def send_chat_message(self, message):
        if self.chat_app:
            self.chat_app.ids.message_input.text = message
            self.chat_app.send_message()
        else:
            logging.warning("Chat interface is not available.")

# --- مثال على الاستخدام ---

if __name__ == "__main__":
    # مثال لإعداد الألوان (للكشف عن شيء أزرق فاتح، مثل مؤشر في لعبة)
    # هذه القيم تحتاج إلى تعديل حسب الألوان الفعلية في البيئة المستهدفة.
    # استخدم أداة مثل color picker في GIMP أو Photoshop أو أدوات أخرى للبحث عن نطاقات HSV.
    # مثال: لون أزرق فاتح: HSV ~ (100-130, 100-255, 50-255)
    # هنا نستخدم نطاق واسع لتمثيل الأعداء
    DEFAULT_ENEMY_COLOR_LOWER = (0, 100, 50)  # Hue, Saturation, Value
    DEFAULT_ENEMY_COLOR_UPPER = (180, 255, 255)

    # استبدل '0' بمسار ملف فيديو إذا كنت تريد تحليل ملف بدلاً من الكاميرا
    # مثال: video_source = "my_gameplay.mp4"
    video_source = 0 # 0 للكاميرا الافتراضية

    print("Initializing Core Logic...")
    core = CoreLogic(screen_width=1280, screen_height=720,
                     enemy_color_lower=DEFAULT_ENEMY_COLOR_LOWER,
                     enemy_color_upper=DEFAULT_ENEMY_COLOR_UPPER)

    # بدء تشغيل النظام
    core.start()

    print("CoreLogic system started.")
    print("Available commands:")
    print("  start_training")
    print("  stop_training")
    print("  start_capture <filename.avi>")
    print("  stop_capture")
    print("  analyze_file <video_path> [output_filename.avi]")
    print("  simulate_click <x> <y>")
    print("  send_chat <message>")
    print("  stop_system")
    print("  quit")

    try:
        while True:
            command = input("Enter command: ").strip().split()
            if not command:
                continue

            cmd = command[0].lower()

            if cmd == "start_training":
                core.start_training_session()
                print("Training session started.")
            elif cmd == "stop_training":
                core.stop_training_session()
                print("Training session stopped.")
            elif cmd == "start_capture":
                filename = command[1] if len(command) > 1 else "capture.avi"
                core.start_video_capture(filename)
                print(f"Video capture started, saving to {filename}.")
            elif cmd == "stop_capture":
                core.stop_video_capture()
                print("Video capture stopped.")
            elif cmd == "analyze_file":
                if len(command) < 2:
                    print("Usage: analyze_file <video_path> [output_filename.avi]")
                    continue
                video_path = command[1]
                output_filename = command[2] if len(command) > 2 else "processed_video.avi"
                core.analyze_video_file(video_path, output_filename)
                print(f"Analyzing {video_path}, output to {output_filename}.")
            elif cmd == "simulate_click":
                if len(command) < 3:
                    print("Usage: simulate_click <x> <y>")
                    continue
                try:
                    x, y = int(command[1]), int(command[2])
                    core.simulate_click((x, y))
                    print(f"Simulated click at ({x}, {y}).")
                except ValueError:
                    print("Invalid coordinates. Please provide integers for x and y.")
            elif cmd == "send_chat":
                if len(command) < 2:
                    print("Usage: send_chat <message>")
                    continue
                message = " ".join(command[1:])
                core.send_chat_message(message)
                print(f"Sent chat message: '{message}'")
            elif cmd == "stop_system":
                core.stop()
                print("CoreLogic system stopped.")
                break
            elif cmd == "quit":
                core.stop()
                print("Exiting.")
                break
            else:
                print(f"Unknown command: {cmd}")
    except KeyboardInterrupt:
        print("\nInterrupted by user. Stopping system.")
        core.stop()
    finally:
        # تأكد من إغلاق جميع العمليات بشكل صحيح
        if core.running:
            core.stop()
        if KIVY_AVAILABLE and core.chat_app:
            # Kivy's App.run() blocks, so if we are here it means we exited the loop
            # or KeyboardInterrupt happened. Kivy itself might handle cleanup,
            # but explicit closing might be needed for certain scenarios.
            pass # Usually Kivy handles shutdown signals well