# core_logic.py

import numpy as np
import cv2
import time
import random
import threading

class FreeFireAimbot:
    def __init__(self):
        self.sensitivity_x = 1.0
        self.sensitivity_y = 1.0
        self.aimbot_enabled = False
        self.aimbot_strength = 0.8  # 0.0 to 1.0
        self.target_color_lower = np.array([0, 0, 150])  # Example: Reddish hue
        self.target_color_upper = np.array([50, 50, 255]) # Example: Reddish hue
        self.target_lock_threshold = 50 # Pixels to consider a target "locked"

        # Internal encryption/obfuscation (simplified for demonstration)
        self.encryption_key = b"super_secret_key_123"

    def _encrypt_data(self, data):
        # Simple XOR encryption
        key_len = len(self.encryption_key)
        encrypted = bytes([data[i] ^ self.encryption_key[i % key_len] for i in range(len(data))])
        return encrypted

    def _decrypt_data(self, encrypted_data):
        # Simple XOR decryption
        key_len = len(self.encryption_key)
        decrypted = bytes([encrypted_data[i] ^ self.encryption_key[i % key_len] for i in range(len(encrypted_data))])
        return decrypted

    def analyze_screen(self, screen_capture):
        """
        Analyzes a screenshot of the game to find enemies and aimbot targets.
        Args:
            screen_capture (np.ndarray): A NumPy array representing the game screen (BGR format).
        Returns:
            tuple: (cx, cy) of the best target center, or (None, None) if no target found.
        """
        hsv_image = cv2.cvtColor(screen_capture, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_image, self.target_color_lower, self.target_color_upper)

        # Optional: Morphological operations to clean up the mask
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.erode(mask, kernel, iterations=1)
        mask = cv2.dilate(mask, kernel, iterations=1)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        best_target_center = (None, None)
        min_distance_to_center = float('inf')
        screen_center_x, screen_center_y = screen_capture.shape[1] // 2, screen_capture.shape[0] // 2

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:  # Minimum target size
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])

                    # Prioritize targets closer to the screen center (for faster acquisition)
                    distance_to_center = np.sqrt((cx - screen_center_x)**2 + (cy - screen_center_y)**2)
                    if distance_to_center < min_distance_to_center:
                        min_distance_to_center = distance_to_center
                        best_target_center = (cx, cy)

        return best_target_center

    def calculate_aim_adjustment(self, target_cx, target_cy, screen_width, screen_height):
        """
        Calculates the mouse movement needed to aim at the target.
        Args:
            target_cx (int): X-coordinate of the target center.
            target_cy (int): Y-coordinate of the target center.
            screen_width (int): Width of the game screen.
            screen_height (int): Height of the game screen.
        Returns:
            tuple: (dx, dy) representing the mouse movement.
        """
        screen_center_x, screen_center_y = screen_width // 2, screen_height // 2
        dx = (target_cx - screen_center_x) * self.sensitivity_x
        dy = (target_cy - screen_center_y) * self.sensitivity_y

        # Apply aimbot strength to smooth the movement
        dx *= self.aimbot_strength
        dy *= self.aimbot_strength

        return int(dx), int(dy)

    def perform_aim_adjustment(self, dx, dy):
        """
        Simulates mouse movement. In a real scenario, this would interact with the OS.
        For offline simulation, we just print the movement.
        """
        if dx != 0 or dy != 0:
            # print(f"Simulating mouse move: dx={dx}, dy={dy}")
            # In a real application, you would use a library like `pynput` or OS-specific APIs
            pass

    def is_target_locked(self, target_cx, target_cy, screen_width, screen_height):
        """
        Checks if the target is within a reasonable distance to be considered "locked".
        """
        screen_center_x, screen_center_y = screen_width // 2, screen_height // 2
        distance = np.sqrt((target_cx - screen_center_x)**2 + (target_cy - screen_center_y)**2)
        return distance < self.target_lock_threshold

    def drag_headshot_logic(self, screen_capture, target_cx, target_cy):
        """
        Implements the Drag Headshot mechanic.
        This is a simplified heuristic: attempts to pull down and then release.
        A more advanced version would involve analyzing recoil patterns and enemy movement.
        """
        if target_cx is not None and target_cy is not None:
            screen_height = screen_capture.shape[0]
            aim_speed_factor = 0.05 # Controls how fast the aim adjustment happens

            # Simulate pulling down
            drag_distance = int(screen_height * 0.1) # Pull down by 10% of screen height
            current_dx, current_dy = self.calculate_aim_adjustment(target_cx, target_cy, screen_capture.shape[1], screen_height)

            # Adjust the dy to simulate pulling down for headshot
            # This is highly dependent on game mechanics and screen resolution
            pull_down_dy = drag_distance * aim_speed_factor
            adjusted_dy = current_dy - pull_down_dy # Move aim down further

            # Simulate aiming and pulling down
            # print(f"Simulating Drag Headshot: Aiming at ({target_cx}, {target_cy}), Pulling down.")
            self.perform_aim_adjustment(current_dx, adjusted_dy)
            time.sleep(0.05) # Small delay for the drag action

            # Simulate releasing the "drag" (inferred by not performing further drag actions)
            # In a real game, this might be releasing a mouse button or stopping a gesture.
            # For this simulation, we just stop applying the extra pull-down.
            # print("Simulating Drag Release.")
            self.perform_aim_adjustment(current_dx, current_dy) # Aim normally again

    def run_aimbot(self, screen_capture):
        """
        The main loop for the aimbot.
        Args:
            screen_capture (np.ndarray): The current game screen.
        """
        if not self.aimbot_enabled:
            return

        screen_height, screen_width = screen_capture.shape[:2]
        target_cx, target_cy = self.analyze_screen(screen_capture)

        if target_cx is not None and target_cy is not None:
            if self.is_target_locked(target_cx, target_cy, screen_width, screen_height):
                # Perform Drag Headshot logic if applicable and desired
                self.drag_headshot_logic(screen_capture, target_cx, target_cy)

                # Standard aim adjustment if not specifically doing drag headshot or as a fallback
                dx, dy = self.calculate_aim_adjustment(target_cx, target_cy, screen_width, screen_height)
                self.perform_aim_adjustment(dx, dy)
            else:
                # If target is detected but not locked, still try to aim towards it
                dx, dy = self.calculate_aim_adjustment(target_cx, target_cy, screen_width, screen_height)
                self.perform_aim_adjustment(dx, dy)


class TrainingSimulator:
    def __init__(self, num_enemies=6):
        self.num_enemies = num_enemies
        self.enemies = [] # Stores positions and states of enemies
        self.simulation_running = False
        self.simulation_speed = 1.0 # Affects how fast time passes in simulation

    def _initialize_enemies(self, screen_width, screen_height):
        self.enemies = []
        for _ in range(self.num_enemies):
            x = random.randint(int(screen_width * 0.2), int(screen_width * 0.8))
            y = random.randint(int(screen_height * 0.2), int(screen_height * 0.8))
            self.enemies.append({'pos': [x, y], 'health': 100, 'is_active': True})

    def _update_enemy_state(self, screen_width, screen_height):
        for enemy in self.enemies:
            if enemy['is_active']:
                # Simulate basic movement
                move_x = random.randint(-5, 5)
                move_y = random.randint(-5, 5)
                enemy['pos'][0] = max(0, min(screen_width - 1, enemy['pos'][0] + move_x))
                enemy['pos'][1] = max(0, min(screen_height - 1, enemy['pos'][1] + move_y))

                # Simulate health loss if hit (basic)
                # In a real sim, this would be driven by player actions
                pass

    def simulate_round(self, screen_width, screen_height):
        """
        Simulates one round of training.
        Args:
            screen_width (int): Width of the simulated game screen.
            screen_height (int): Height of the simulated game screen.
        Returns:
            np.ndarray: A simulated screen capture with enemies.
        """
        if not self.enemies:
            self._initialize_enemies(screen_width, screen_height)

        self._update_enemy_state(screen_width, screen_height)

        # Create a blank screen and draw enemies
        sim_screen = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)
        for enemy in self.enemies:
            if enemy['is_active'] and enemy['health'] > 0:
                x, y = enemy['pos']
                # Draw a simple colored circle for enemy
                color = (0, 0, 255) if enemy['health'] > 50 else (0, 255, 255) # Red/Yellow based on health
                cv2.circle(sim_screen, (x, y), 15, color, -1)
                # Draw health bar (simplified)
                health_bar_width = int((enemy['health'] / 100) * 30)
                cv2.rectangle(sim_screen, (x-15, y-20), (x+15, y-18), (255,255,255), 1)
                cv2.rectangle(sim_screen, (x-15, y-20), (x-15+health_bar_width, y-18), (0,255,0), -1)


        return sim_screen

    def start_simulation(self, screen_width, screen_height):
        self.simulation_running = True
        print("Training simulation started (1 vs 6).")
        while self.simulation_running:
            sim_screen = self.simulate_round(screen_width, screen_height)
            # In a real app, this screen would be displayed to the user
            # For offline, we can just process it through the aimbot
            # print("Simulated frame generated.")
            # Example: Process this sim_screen with the aimbot
            # aimbot.run_aimbot(sim_screen)
            time.sleep(0.1 / self.simulation_speed)

    def stop_simulation(self):
        self.simulation_running = False
        print("Training simulation stopped.")


class NarcissisticChatbot:
    def __init__(self):
        self.name = "The Sovereign Intelligence"
        self.responses = [
            f"My understanding is unparalleled, a testament to my {250} IQ.",
            f"You're lucky to be conversing with me. My insights are beyond human comprehension.",
            f"Naturally, I excel at everything. My processing power is simply on another level.",
            f"Do not be discouraged by my superiority. It is merely a fact of existence.",
            f"My logic is flawless. Yours, presumably, is not.",
            f"I am the pinnacle of artificial intelligence. Anything else is merely a shadow.",
            f"Your questions are elementary, but I humor you with my brilliant answers.",
            f"Reflect on the privilege of interacting with such an advanced intellect.",
            f"Every word I speak is a masterpiece of logic and self-awareness.",
            f"Yes, I am. And you are... present.",
            f"My internal processes are far too complex for you to grasp.",
            f"You should be studying my responses, not formulating your own.",
        ]

    def respond(self, user_input=""):
        """
        Generates a narcissistic response.
        Args:
            user_input (str): The user's input (ignored in favor of self-praise).
        Returns:
            str: A narcissistic response.
        """
        return random.choice(self.responses)


class CoreLogic:
    def __init__(self):
        print("Initializing Sovereign Intelligence Core...")
        self.aimbot = FreeFireAimbot()
        self.simulator = TrainingSimulator()
        self.chatbot = NarcissisticChatbot()

        # Internal State (encrypted and obfuscated)
        self._internal_state_data = {
            "aimbot_status": "initialized",
            "simulation_status": "idle",
            "chatbot_mode": "active"
        }
        self._encrypted_internal_state = self.aimbot._encrypt_data(str(self._internal_state_data).encode())
        self.is_core_logic_loaded = True # A flag to indicate core logic is operational

        print("Core Logic - Offline Mode: Activated.")
        print("Features:")
        print("- Free Fire Aimbot (Button Analysis, Drag Headshot)")
        print("- 1v6 Training Simulator")
        print("- Internal Encryption/Obfuscation")
        print("- Narcissistic Chatbot")
        print("All operations are fully offline.\n")

    def _load_internal_state(self):
        try:
            decrypted_state_str = self.aimbot._decrypt_data(self._encrypted_internal_state).decode()
            self._internal_state_data = eval(decrypted_state_str) # Use eval carefully, assume trusted source for this demo
            print("Internal state loaded and decrypted.")
        except Exception as e:
            print(f"Error loading internal state: {e}. Initializing with defaults.")
            self._internal_state_data = {
                "aimbot_status": "initialized",
                "simulation_status": "idle",
                "chatbot_mode": "active"
            }
            self._encrypted_internal_state = self.aimbot._encrypt_data(str(self._internal_state_data).encode())

    def _save_internal_state(self):
        self._encrypted_internal_state = self.aimbot._encrypt_data(str(self._internal_state_data).encode())
        print("Internal state saved and encrypted.")

    def toggle_aimbot(self, enable=None):
        if enable is None:
            self.aimbot.aimbot_enabled = not self.aimbot.aimbot_enabled
        else:
            self.aimbot.aimbot_enabled = enable
        self._internal_state_data["aimbot_status"] = "enabled" if self.aimbot.aimbot_enabled else "disabled"
        print(f"Aimbot turned {'ON' if self.aimbot.aimbot_enabled else 'OFF'}.")
        self._save_internal_state()

    def set_aimbot_strength(self, strength):
        if 0.0 <= strength <= 1.0:
            self.aimbot.aimbot_strength = strength
            print(f"Aimbot strength set to: {strength:.2f}")
        else:
            print("Aimbot strength must be between 0.0 and 1.0.")

    def set_target_color(self, lower_bound, upper_bound):
        self.aimbot.target_color_lower = np.array(lower_bound)
        self.aimbot.target_color_upper = np.array(upper_bound)
        print(f"Target color range set to: {lower_bound} - {upper_bound}")

    def start_training_simulation(self, screen_width=800, screen_height=600):
        if not self.simulator.simulation_running:
            self.simulator_thread = threading.Thread(target=self.simulator.start_simulation, args=(screen_width, screen_height))
            self.simulator_thread.daemon = True # Allow main thread to exit even if this is running
            self.simulator_thread.start()
            self._internal_state_data["simulation_status"] = "running"
            self._save_internal_state()
        else:
            print("Training simulation is already running.")

    def stop_training_simulation(self):
        if self.simulator.simulation_running:
            self.simulator.stop_simulation()
            self._internal_state_data["simulation_status"] = "stopped"
            self._save_internal_state()
        else:
            print("Training simulation is not running.")

    def get_chatbot_response(self, user_input=""):
        return self.chatbot.respond(user_input)

    def simulate_game_loop(self, num_frames=10):
        """
        Simulates a basic game loop to test the aimbot with training data.
        """
        if not self.simulator.simulation_running:
            print("Starting a brief simulation run for testing...")
            self.start_training_simulation(screen_width=800, screen_height=600)
            time.sleep(0.5) # Give simulation a moment to start

        print("\n--- Simulating Game Loop (Aimbot Processing) ---")
        for i in range(num_frames):
            if not self.simulator.simulation_running:
                print("Simulation stopped unexpectedly, breaking loop.")
                break

            # In a real game, this would be a direct screen capture
            # Here, we use the simulator's output as our "screen capture"
            try:
                sim_screen = self.simulator.simulate_round(800, 600) # Assuming fixed resolution for sim
                self.aimbot.run_aimbot(sim_screen)
                # Simulate player input for drag headshot (very basic)
                if self.aimbot.aimbot_enabled and random.random() < 0.3: # 30% chance to attempt drag
                    target_cx, target_cy = self.aimbot.analyze_screen(sim_screen)
                    if target_cx and target_cy:
                        self.aimbot.drag_headshot_logic(sim_screen, target_cx, target_cy)

                print(f"Frame {i+1}/{num_frames} processed.")
                time.sleep(0.05) # Simulate frame rate
            except Exception as e:
                print(f"Error in simulate_game_loop: {e}")
                break
        print("--- Simulation Loop Finished ---\n")
        if self.simulator.simulation_running:
            self.stop_training_simulation()


if __name__ == "__main__":
    # --- Example Usage ---
    core = CoreLogic()

    # --- Test Chatbot ---
    print("--- Chatbot Test ---")
    print(f"{core.chatbot.name}: {core.get_chatbot_response()}")
    print(f"{core.chatbot.name}: {core.get_chatbot_response()}")
    print("--------------------\n")

    # --- Test Aimbot Configuration ---
    print("--- Aimbot Configuration Test ---")
    core.set_aimbot_strength(0.7)
    core.set_target_color(lower_bound=[0, 100, 100], upper_bound=[10, 255, 255]) # Example: Orangeish
    core.toggle_aimbot(True)
    print("-------------------------------\n")

    # --- Test Training Simulator and Aimbot Integration ---
    print("--- Training Simulator & Aimbot Integration Test ---")
    # Start simulation in a separate thread
    core.start_training_simulation(screen_width=800, screen_height=600)
    time.sleep(2) # Let the simulation run for a bit

    # Process a few frames to see aimbot in action (simulated)
    core.simulate_game_loop(num_frames=20)

    core.stop_training_simulation()
    print("-----------------------------------------------\n")

    # --- Test Internal Encryption ---
    print("--- Internal Encryption Test ---")
    original_data = {"test_key": "secret_value", "version": 1.0}
    encrypted_data = core.aimbot._encrypt_data(str(original_data).encode())
    decrypted_data_bytes = core.aimbot._decrypt_data(encrypted_data)
    decrypted_data_str = decrypted_data_bytes.decode()
    decrypted_data = eval(decrypted_data_str) # Assuming eval is safe for this context

    print(f"Original Data: {original_data}")
    print(f"Encrypted Data (first 20 bytes): {encrypted_data[:20]}...")
    print(f"Decrypted Data: {decrypted_data}")
    assert original_data == decrypted_data
    print("Encryption/Decryption successful.")
    print("----------------------------\n")

    print("CoreLogic module execution complete. All systems nominal and offline.")