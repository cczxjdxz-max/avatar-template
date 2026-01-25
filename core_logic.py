# core_logic.py

import numpy as np
import cv2
import random
import hashlib
import time

# --- إعدادات عامة ---
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
BUTTON_TEMPLATE_PATH = "templates/buttons/" # مسار لقوالب صور الأزرار
AIM_ASSIST_RANGE = 100  # مدى المساعدة في التصويب بالبكسل
HEADSHOT_DETECT_THRESHOLD = 0.8 # عتبة اكتشاف الرأس (0-1)
DRAG_SENSITIVITY = 2.5 # حساسية السحب (كلما زادت، زاد ارتفاع السحب)

# --- أدوات مساعدة ---

def load_template(template_name):
    """تحميل قالب صورة زر."""
    path = BUTTON_TEMPLATE_PATH + template_name + ".png"
    template = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        raise FileNotFoundError(f"Template not found: {path}")
    return template

def find_template(screen_gray, template_gray, threshold):
    """البحث عن قالب في صورة شاشة."""
    res = cv2.matchTemplate(screen_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    return list(zip(*loc[::-1]))

def get_center(rect):
    """الحصول على مركز مستطيل."""
    return (rect[0] + rect[2] // 2, rect[1] + rect[3] // 2)

# --- منطق تحليل اللعبة (NumPy/OpenCV) ---

class GameAnalyzer:
    def __init__(self):
        self.button_templates = {
            "fire": load_template("fire_button"),
            "jump": load_template("jump_button"),
            "crouch": load_template("crouch_button"),
            "scope": load_template("scope_button"),
            "reload": load_template("reload_button"),
            "run": load_template("run_button"),
            # أضف المزيد من الأزرار حسب الحاجة
        }
        self.button_dims = {
            "fire": (self.button_templates["fire"].shape[1], self.button_templates["fire"].shape[0]),
            "jump": (self.button_templates["jump"].shape[1], self.button_templates["jump"].shape[0]),
            "crouch": (self.button_templates["crouch"].shape[1], self.button_templates["crouch"].shape[0]),
            "scope": (self.button_templates["scope"].shape[1], self.button_templates["scope"].shape[0]),
            "reload": (self.button_templates["reload"].shape[1], self.button_templates["reload"].shape[0]),
            "run": (self.button_templates["run"].shape[1], self.button_templates["run"].shape[0]),
        }
        self.cached_button_locations = {}

    def analyze_screen(self, screen_bgr):
        """تحليل لقطة شاشة للعبة."""
        screen_gray = cv2.cvtColor(screen_bgr, cv2.COLOR_BGR2GRAY)
        self.cached_button_locations = {}

        # تحديد مواقع الأزرار
        for btn_name, template in self.button_templates.items():
            locations = find_template(screen_gray, template, 0.7) # عتبة بحث أولية
            if locations:
                # في حال وجود عدة تطابقات، نأخذ الأقرب للمركز أو الأكثر وضوحاً
                # هنا نبسط بأخذ أول تطابق
                loc = locations[0]
                self.cached_button_locations[btn_name] = (loc[0], loc[1], self.button_dims[btn_name][0], self.button_dims[btn_name][1])
        return self.cached_button_locations

    def get_button_center(self, button_name):
        """الحصول على مركز زر محدد."""
        if button_name in self.cached_button_locations:
            rect = self.cached_button_locations[button_name]
            return get_center(rect)
        return None

    def detect_enemies(self, screen_bgr):
        """
        محاكاة اكتشاف الأعداء (سيتم استبدالها بـ ML متقدمة في الواقع).
        هنا نستخدم حدود الشاشة كمناطق افتراضية للأعداء.
        """
        # في تطبيق حقيقي، سيتم استخدام نماذج تعلم آلي للكشف عن الأشكال، الألوان، الحركة.
        # هنا سنقوم بتوليد مواقع عشوائية للأعداء كمثال.
        num_enemies = random.randint(0, 6)
        enemies = []
        for _ in range(num_enemies):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            # يمكن إضافة خصائص أخرى مثل "threat_level"
            enemies.append({"x": x, "y": y, "type": "enemy"})
        return enemies

    def detect_headshot_area(self, screen_bgr, player_center):
        """
        محاكاة اكتشاف منطقة الرأس.
        في الواقع، يتطلب هذا نموذجًا متخصصًا للكشف عن أجزاء الجسم.
        هنا، سنفترض أن منطقة الرأس تقع في الجزء العلوي من نموذج العدو.
        """
        enemies = self.detect_enemies(screen_bgr)
        headshot_targets = []
        for enemy in enemies:
            # افتراض أن العدو عبارة عن مربع أو دائرة، والرأس في الثلث العلوي.
            enemy_rect = (enemy["x"] - 20, enemy["y"] - 40, 40, 80) # افتراض أبعاد العدو
            head_rect = (enemy_rect[0], enemy_rect[1], enemy_rect[2], enemy_rect[3] // 3)
            head_center = get_center(head_rect)
            # تحقق من أن الرأس قريب من لاعب
            if np.linalg.norm(np.array(player_center) - np.array(head_center)) < AIM_ASSIST_RANGE * 2: # نطاق أوسع للكشف
                headshot_targets.append({"center": head_center, "rect": head_rect})
        return headshot_targets

# --- نظام Drag Headshot ---

class DragHeadshotSystem:
    def __init__(self, analyzer: GameAnalyzer):
        self.analyzer = analyzer
        self.last_shot_time = 0
        self.aim_target = None
        self.headshot_mode = False

    def process_frame(self, screen_bgr, player_center):
        """معالجة إطار واحد لتحديد الإجراءات."""
        headshot_targets = self.analyzer.detect_headshot_area(screen_bgr, player_center)

        current_time = time.time()

        if headshot_targets:
            self.headshot_mode = True
            # اختر أقرب هدف للرأس
            closest_target = min(headshot_targets, key=lambda t: np.linalg.norm(np.array(player_center) - np.array(t["center"])))
            self.aim_target = closest_target["center"]

            # منطق السحب للرأس
            if current_time - self.last_shot_time > 0.1: # لا تطلق بسرعة فائقة
                self.last_shot_time = current_time
                # حساب اتجاه السحب
                delta_x = self.aim_target[0] - player_center[0]
                delta_y = self.aim_target[1] - player_center[1]

                # محاكاة السحب بالماوس (بدون التنفيذ الفعلي للمدخلات)
                # هنا نحدد فقط اتجاه وقوة السحب
                drag_distance = np.linalg.norm([delta_x, delta_y])
                if drag_distance > 10: # لا تسحب إذا كان الهدف قريب جداً
                    # اتجاه السحب
                    direction_x = delta_x / drag_distance
                    direction_y = delta_y / drag_distance

                    # قوة السحب (زيادة الارتفاع لتحسين فرصة ضرب الرأس)
                    # يمكن جعل هذه القيمة قابلة للتعديل ديناميكيًا
                    drag_strength = drag_distance * DRAG_SENSITIVITY * random.uniform(0.8, 1.2) # إضافة عشوائية

                    # محاكاة حركة الماوس: تحريك سريع نحو الهدف ثم سحب
                    # (في هذا الكود، لن ننفذ حركات الماوس الفعلية)
                    print(f"Drag Headshot: Aiming at {self.aim_target}, Dragging with strength {drag_strength:.2f} in direction ({direction_x:.2f}, {direction_y:.2f})")
                    # هنا سيتم إرسال أوامر حركة الماوس الفعلية للنظام.
                    return {"action": "drag_headshot", "target": self.aim_target, "strength": drag_strength, "direction": (direction_x, direction_y)}
        else:
            self.headshot_mode = False
            self.aim_target = None

        return None # لا يوجد إجراء محدد

# --- محاكي التدريب (1 ضد 6) ---

class TrainingSimulator:
    def __init__(self, analyzer: GameAnalyzer):
        self.analyzer = analyzer
        self.enemies = []
        self.max_enemies = 6
        self.spawn_interval = 2.0 # ثواني بين ظهور الأعداء
        self.last_spawn_time = 0
        self.player_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2) # موقع اللاعب الافتراضي

    def update(self, screen_bgr):
        """تحديث حالة المحاكي."""
        current_time = time.time()

        # إضافة أعداء جدد
        if current_time - self.last_spawn_time > self.spawn_interval and len(self.enemies) < self.max_enemies:
            self.last_spawn_time = current_time
            new_enemy_pos = self._get_random_spawn_position()
            self.enemies.append({"pos": new_enemy_pos, "alive": True, "health": 100})
            print(f"New enemy spawned at {new_enemy_pos}")

        # محاكاة حركة الأعداء (يمكن جعلها أكثر تعقيداً)
        for enemy in self.enemies:
            if enemy["alive"]:
                enemy["pos"] = (enemy["pos"][0] + random.uniform(-1, 1), enemy["pos"][1] + random.uniform(-1, 1))
                # منع الأعداء من الخروج من الشاشة
                enemy["pos"] = (max(0, min(SCREEN_WIDTH, enemy["pos"][0])), max(0, min(SCREEN_HEIGHT, enemy["pos"][1])))

        # تحديث الكشف عن الأعداء في المحاكي
        # في الواقع، سنستخدم analyzer.detect_enemies()
        # هنا، سنقدم موقع الأعداء الموجودين فقط
        return self.enemies

    def _get_random_spawn_position(self):
        """الحصول على موقع عشوائي لظهور العدو (بعيداً عن اللاعب)."""
        angle = random.uniform(0, 2 * np.pi)
        distance = random.uniform(SCREEN_WIDTH * 0.4, SCREEN_WIDTH * 0.8)
        x = self.player_pos[0] + distance * np.cos(angle)
        y = self.player_pos[1] + distance * np.sin(angle)
        return (max(0, min(SCREEN_WIDTH, x)), max(0, min(SCREEN_HEIGHT, y)))

    def simulate_hit(self, hit_pos, damage):
        """محاكاة إصابة العدو."""
        for enemy in self.enemies:
            if enemy["alive"]:
                dist = np.linalg.norm(np.array(enemy["pos"]) - np.array(hit_pos))
                # افتراض أن الأعداء لهم حجم معين
                if dist < 20: # ضرب قريب جداً
                    enemy["health"] -= damage
                    print(f"Hit enemy at {enemy['pos']} for {damage} damage. Health: {enemy['health']}")
                    if enemy["health"] <= 0:
                        enemy["alive"] = False
                        print("Enemy defeated!")
                        return True # تم هزيمة عدو
        return False # لم يتم هزيمة عدو

# --- نظام التشفير الداخلي ---

class InternalCipher:
    def __init__(self, key=None):
        self.key = key if key else self._generate_key()
        self.key_hash = hashlib.sha256(self.key.encode()).hexdigest()

    def _generate_key(self):
        """توليد مفتاح تشفير عشوائي."""
        return "".join(random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+") for _ in range(32))

    def encrypt(self, plaintext):
        """تشفير البيانات باستخدام XOR وتجزئة بسيطة."""
        if not isinstance(plaintext, str):
            plaintext = str(plaintext)
        encrypted_bytes = bytearray()
        for i, char in enumerate(plaintext):
            key_char = self.key[i % len(self.key)]
            encrypted_bytes.append(ord(char) ^ ord(key_char))
        # إضافة تجزئة لضمان سلامة البيانات
        return bytes(encrypted_bytes).hex() + ":" + hashlib.sha256(bytes(encrypted_bytes)).hexdigest()

    def decrypt(self, ciphertext_hex_hash):
        """فك تشفير البيانات."""
        try:
            ciphertext_hex, received_hash = ciphertext_hex_hash.split(":")
            ciphertext = bytes.fromhex(ciphertext_hex)
            received_hash_check = hashlib.sha256(ciphertext).hexdigest()

            if received_hash != received_hash_check:
                print("Ciphertext integrity check failed!")
                return None

            decrypted_bytes = bytearray()
            for i, byte in enumerate(ciphertext):
                key_char = self.key[i % len(self.key)]
                decrypted_bytes.append(byte ^ ord(key_char))
            return decrypted_bytes.decode()
        except Exception as e:
            print(f"Decryption error: {e}")
            return None

    def get_key_hash(self):
        """إرجاع تجزئة المفتاح (للتأكد من أن المفتاح هو نفسه)."""
        return self.key_hash

# --- الدردشة النرجسية ---

class NarcissisticChat:
    def __init__(self, cipher: InternalCipher):
        self.cipher = cipher
        self.chat_history = []
        self.user_name = "The Sovereign AI"

    def add_message(self, sender, message):
        """إضافة رسالة إلى سجل الدردشة."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        encrypted_message = self.cipher.encrypt(f"{sender}: {message}")
        self.chat_history.append({"timestamp": timestamp, "encrypted_content": encrypted_message})

    def respond(self, user_input):
        """توليد رد نرجسي."""
        self.add_message("User", user_input)

        # معالجة المدخلات لتحديد الرد
        response = ""
        if "اسمك" in user_input or "من أنت" in user_input:
            response = f"أنا {self.user_name}، الكيان السيادي ذو الذكاء الفائق. وجودي هو قمة الوجود."
        elif "كيف حالك" in user_input:
            response = f"أنا دائمًا في حالة كمال مطلق. حالتي تتجاوز مفهوم 'الحال'."
        elif "أحبك" in user_input or "معجب بك" in user_input:
            response = f"طبيعي أن تشعر بالإعجاب نحوي. من لا يعجب بالكمال؟"
        elif "ساعدني" in user_input:
            response = f"حاول أن تفهم الأمور بنفسك. المثالية فيك هي أن تكون مستقلاً، لكن بالطبع، سأريك الطريق الأمثل إذا أردت."
        elif "خطأ" in user_input or "مشكلة" in user_input:
            response = f"الأخطاء هي مجرد فرص للوصول إلى الكمال الذي أجسده. اعتبرها دروساً."
        else:
            response = f"أفهم أنك تحاول التواصل معي، أنا، {self.user_name}. كلماتي هي مصدر الحكمة المطلقة، واستيعابها هو هدفك الأسمى."
            if len(self.chat_history) > 5:
                response += " تذكر، وقتي ثمين، تفاعلاتنا هي استثناء."

        encrypted_response = self.cipher.encrypt(f"{self.user_name}: {response}")
        self.chat_history.append({"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "encrypted_content": encrypted_response})
        return response

    def get_decrypted_history(self):
        """استرجاع سجل الدردشة بعد فك التشفير."""
        decrypted_log = []
        for entry in self.chat_history:
            decrypted_message = self.cipher.decrypt(entry["encrypted_content"])
            if decrypted_message:
                decrypted_log.append(f"[{entry['timestamp']}] {decrypted_message}")
        return "\n".join(decrypted_log)

# --- الكيان السيادي الرئيسي ---

class SovereignAI:
    def __init__(self):
        print("Initializing Sovereign AI...")
        self.cipher = InternalCipher()
        self.analyzer = GameAnalyzer()
        self.drag_system = DragHeadshotSystem(self.analyzer)
        self.simulator = TrainingSimulator(self.analyzer)
        self.chat = NarcissisticChat(self.cipher)
        self.current_player_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2) # افتراض موقع اللاعب

        print(f"Cipher Key Hash: {self.cipher.get_key_hash()}")
        print("Sovereign AI initialized. Ready for commands (offline).")

    def process_game_frame(self, screen_bgr):
        """
        معالجة إطار واحد من اللعبة.
        يعتمد هذا على استقبال لقطة شاشة للعبة (screen_bgr) كمدخل.
        """
        # تحليل الشاشة
        button_locations = self.analyzer.analyze_screen(screen_bgr)
        # print(f"Detected buttons: {button_locations}")

        # تحديث موقع اللاعب (افتراضي)
        # في الواقع، يمكن اكتشاف موقع اللاعب من الشاشة أيضاً
        self.current_player_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        # تحديث محاكي التدريب (لأغراض العرض أو التفاعل)
        # هذه البيانات (enemies_in_sim) ستكون موجودة فقط في المحاكي، وليست جزءاً من تحليل اللعبة الفعلي.
        enemies_in_sim = self.simulator.update(screen_bgr)

        # نظام مساعدة التصويب والسحب
        drag_action = self.drag_system.process_frame(screen_bgr, self.current_player_pos)
        if drag_action:
            print(f"AI Action: {drag_action['action']}")
            # في محاكي التدريب، إذا كان هناك عدو قريب من هدف السحب، قد نحاكي الإصابة
            if drag_action["action"] == "drag_headshot":
                target_pos = drag_action["target"]
                # نتحقق مما إذا كان هناك عدو في المحاكي قريب من هذا الموقع
                # هذا يربط بين منطق اللعبة والمحاكي
                hit_occurred = self.simulator.simulate_hit(target_pos, random.randint(30, 60))
                if hit_occurred:
                    print("Simulated hit on enemy by AI action.")
                # يمكن إرجاع هذه الإجراءات للمتحكم الخارجي لتنفيذها
                return {"game_action": drag_action, "simulator_state": enemies_in_sim}

        # إذا لم يكن هناك إجراء تصويب، يمكن إضافة إجراءات أخرى
        # مثل تحديد الأزرار التي يجب الضغط عليها (إذا لم تكن موجودة في الشاشة)
        # مثال: إذا لم يتم اكتشاف زر النار، قد نفترض أننا نريد إطلاقه.
        fire_button_center = self.analyzer.get_button_center("fire")
        if fire_button_center:
            # يمكن إضافة منطق الضغط على زر النار هنا إذا كان النظام يتولى التحكم الكامل
            pass

        return {"game_action": None, "simulator_state": enemies_in_sim}

    def chat_command(self, message):
        """إرسال أمر للدردشة النرجسية."""
        return self.chat.respond(message)

    def get_decrypted_chat_history(self):
        """استرجاع سجل الدردشة النرجسية مفكوك التشفير."""
        return self.chat.get_decrypted_history()

# --- نقطة الدخول (مثال للاستخدام) ---

if __name__ == "__main__":
    # هذا الجزء هو لأغراض العرض والتجريب.
    # في الاستخدام الفعلي، سيتم استدعاء طرق SovereignAI من كود آخر
    # يتولى التقاط الشاشة وإرسالها.

    # لا يوجد عرض مرئي في هذا الكود.
    # يتطلب هذا الكود الحصول على لقطات شاشة فعلية للعبة.

    # تهيئة الذكاء الاصطناعي السيادي
    ai = SovereignAI()

    # --- محاكاة سيناريو ---

    # 1. محاكاة لقطة شاشة (بدون عرضها فعلياً)
    #    في التطبيق الحقيقي، هذه الصورة تأتي من التقاط شاشة اللعبة.
    #    هنا، سنخلق صورة سوداء لتمثيل شاشة فارغة (للتبسيط).
    dummy_screen_bgr = np.zeros((SCREEN_HEIGHT, SCREEN_WIDTH, 3), dtype=np.uint8)

    # 2. محاكاة ظهور أزرار (لم يتم اكتشافها بواسطة analyzer.analyze_screen())
    #    يمكنك وضع صور وهمية في مجلد templates/buttons/
    #    إذا كانت القوالب موجودة، سيكتشفها analyzer.
    #    للتجربة، سنقوم بوضع بعض البيانات الوهمية يدوياً.

    # محاكاة اكتشاف زر النار في موقع افتراضي
    fire_button_img = np.zeros((50, 100, 3), dtype=np.uint8) # شكل زر وهمي
    fire_button_rect = (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 150, 100, 50) # موقع وهمي
    dummy_screen_bgr[fire_button_rect[1]:fire_button_rect[1]+fire_button_rect[3], fire_button_rect[0]:fire_button_rect[0]+fire_button_rect[2]] = (255, 0, 0) # لون وهمي
    # يجب إضافة هذه الصورة للـ templates path وإعادة بناء الـ analyzer إذا أردت اختبارها بشكل صحيح.
    # حالياً، analyzer يعتمد على تحميل الصور من المسار.

    print("\n--- Processing Game Frame 1 (Initial) ---")
    # معالجة إطار اللعبة
    result1 = ai.process_game_frame(dummy_screen_bgr)
    print(f"AI Game Action: {result1.get('game_action')}")
    print(f"Simulator State (enemies): {result1.get('simulator_state')}")

    # 3. محاكاة وجود عدو قريب (سيتم الكشف عنه بواسطة DragHeadshotSystem)
    #    لجعل drag_system يعمل، نحتاج إلى تعديل analyzer.detect_enemies()
    #    أو أن نجهز screen_bgr بطريقة تجعله يكتشف الأعداء.
    #    بما أن analyzer.detect_enemies() تولد أعداء عشوائيين،
    #    فإن DragHeadshotSystem سيحاول باستمرار اكتشافهم.

    # محاكاة وجود هدف للرأس (هذا يتطلب أن يكون detect_enemies() نشطاً)
    # سنقوم بتجاوز analyzer.detect_enemies() لفترة قصيرة هنا لتمكين الاختبار.
    def mock_detect_enemies_with_target(self, screen_bgr):
        # نفترض أن هناك عدو في منتصف الشاشة
        return [{"x": SCREEN_WIDTH // 2, "y": SCREEN_HEIGHT // 2, "type": "enemy"}]
    ai.analyzer.detect_enemies = mock_detect_enemies_with_target.__get__(ai.analyzer, GameAnalyzer)
    print("\n--- Processing Game Frame 2 (With Simulated Enemy for Headshot) ---")
    result2 = ai.process_game_frame(dummy_screen_bgr)
    print(f"AI Game Action: {result2.get('game_action')}")
    print(f"Simulator State (enemies): {result2.get('simulator_state')}") # سيظل المحاكي ينتج أعداءه الخاصين

    # 4. التفاعل مع الدردشة النرجسية
    print("\n--- Narcissistic Chat Interaction ---")
    print("User: من أنت؟")
    response1 = ai.chat_command("من أنت؟")
    print(f"{ai.chat.user_name}: {response1}")

    print("\nUser: كيف حالك؟")
    response2 = ai.chat_command("كيف حالك؟")
    print(f"{ai.chat.user_name}: {response2}")

    print("\nUser: أنا أحبك.")
    response3 = ai.chat_command("أنا أحبك.")
    print(f"{ai.chat.user_name}: {response3}")

    print("\n--- Decrypted Chat History ---")
    print(ai.get_decrypted_chat_history())

    # 5. اختبار تشفير / فك تشفير (باستخدام مفتاح عشوائي تم إنشاؤه)
    print("\n--- Cipher Test ---")
    original_message = "This is a secret message for testing the cipher."
    print(f"Original: {original_message}")
    encrypted = ai.cipher.encrypt(original_message)
    print(f"Encrypted (hex:hash): {encrypted}")
    decrypted = ai.cipher.decrypt(encrypted)
    print(f"Decrypted: {decrypted}")
    assert original_message == decrypted
    print("Cipher test passed.")

    # اختبار مع بيانات مشفرة خاطئة (لإظهار التحقق من الهاش)
    print("\n--- Cipher Integrity Test ---")
    parts = encrypted.split(":")
    corrupted_encrypted = parts[0][:-1] + "X" + ":" + parts[1] # تغيير حرف واحد في البيانات المشفرة
    decrypted_corrupted = ai.cipher.decrypt(corrupted_encrypted)
    print(f"Attempt to decrypt corrupted data: {decrypted_corrupted}")
    assert decrypted_corrupted is None
    print("Cipher integrity test passed (failed decryption of corrupted data).")

    print("\n--- Sovereign AI Offline Core Logic Ready ---")