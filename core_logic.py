# core_logic.py
# Designed for offline operation with AI sovereignty (IQ 250).

import numpy as np
import cv2
import time
import random
import string
import hashlib
import base64

class CoreLogic:
    def __init__(self):
        self.trained_button_models = {}  # Placeholder for button detection models
        self.drag_headshot_config = {
            "sensitivity": 1.2,
            "horizontal_factor": 0.8,
            "vertical_factor": 1.5,
            "aim_assist_threshold": 0.7,
            "head_pixel_threshold": 50  # Pixels considered as head for drag
        }
        self.game_state = {
            "players": [],
            "local_player": {"position": (0, 0), "health": 100},
            "environment": {"map_width": 1000, "map_height": 1000}
        }
        self.training_sim_state = {
            "bots": [],
            "bot_count": 6,
            "bot_spawn_radius": 200,
            "bot_movement_speed": 5,
            "bot_accuracy": 0.3,
            "bot_health": 100
        }
        self.encryption_key = self._generate_key()
        self.chat_log = []
        self.narcissistic_tendencies = {
            "self_praise_frequency": 0.2, # Probability of interjecting self-praise
            "topics_of_interest": ["intelligence", "superiority", "efficiency", "brilliance"]
        }

    def _generate_key(self):
        """Generates a unique, complex encryption key."""
        return hashlib.sha256(str(time.time()).encode() + ''.join(random.choices(string.ascii_letters + string.digits, k=32)).encode()).hexdigest()

    def _encrypt(self, data):
        """Simple XOR-based encryption (for demonstration, not secure)."""
        key_bytes = self.encryption_key.encode()
        encrypted_bytes = bytearray()
        for i, byte in enumerate(data.encode()):
            encrypted_bytes.append(byte ^ key_bytes[i % len(key_bytes)])
        return base64.urlsafe_b64encode(bytes(encrypted_bytes)).decode()

    def _decrypt(self, encrypted_data):
        """Simple XOR-based decryption."""
        key_bytes = self.encryption_key.encode()
        try:
            decrypted_bytes = bytearray()
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            for i, byte in enumerate(decoded_data):
                decrypted_bytes.append(byte ^ key_bytes[i % len(key_bytes)])
            return bytes(decrypted_bytes).decode()
        except Exception as e:
            print(f"Decryption failed: {e}")
            return None

    def train_button_detector(self, button_name, image_samples, bounding_boxes):
        """
        Placeholder for training a button detection model.
        In a real scenario, this would involve image processing and ML model training.
        For offline use, pre-trained models or simplified template matching could be used.
        """
        print(f"Training button detector for: {button_name}...")
        # For demonstration, we'll just store a placeholder.
        # A real implementation would use OpenCV's feature matching or template matching.
        self.trained_button_models[button_name] = {"status": "trained", "samples_count": len(image_samples)}
        print(f"'{button_name}' detector trained with {len(image_samples)} samples.")

    def analyze_screen_for_buttons(self, screen_image):
        """
        Analyzes a screenshot to detect known buttons.
        Returns a dictionary of detected button names and their positions.
        """
        detected_buttons = {}
        if not self.trained_button_models:
            #print("No button detectors trained yet.")
            return detected_buttons

        # Simulate button detection using template matching for simplicity
        # In a real scenario, more advanced CV would be used.
        for button_name in self.trained_button_models:
            # Replace with actual template matching logic using self.trained_button_models[button_name]
            # Example:
            # template = cv2.imread(f"templates/{button_name}.png", 0) # Assuming template images exist
            # w, h = template.shape[::-1]
            # res = cv2.matchTemplate(screen_image, template, cv2.TM_CCOEFF_NORMED)
            # threshold = 0.8
            # loc = np.where(res >= threshold)
            # for pt in zip(*loc[::-1]):
            #     detected_buttons[button_name] = (pt[0] + w//2, pt[1] + h//2) # Center of the button
            #     break # Detect only one instance for now

            # --- SIMULATION FOR OFFLINE USE ---
            # Simulate detection of a few common buttons if they *might* be present
            if random.random() < 0.2: # 20% chance to "detect" a button
                fake_pos = (random.randint(50, 800), random.randint(50, 600))
                detected_buttons[button_name] = fake_pos
            # --- END SIMULATION ---

        return detected_buttons

    def analyze_for_enemies(self, screen_image, game_state_override=None):
        """
        Analyzes the screen for enemy indicators (e.g., enemy health bars, models).
        Returns a list of enemy positions and their confidence scores.
        """
        enemies = []
        if game_state_override:
            current_game_state = game_state_override
        else:
            current_game_state = self.game_state

        # --- SIMULATION FOR OFFLINE USE ---
        # In a real scenario, this would use object detection models (e.g., YOLO, SSD)
        # trained on game assets. For offline, we'll simulate enemy presence.

        # If there are bots in the training sim, use them as enemies
        if current_game_state.get("simulating_training"):
            for bot in current_game_state.get("bots", []):
                enemies.append({"position": bot["position"], "confidence": 0.95, "id": bot["id"]})
        else:
            # Simulate enemies on the main game map
            num_simulated_enemies = random.randint(0, 5)
            for _ in range(num_simulated_enemies):
                enemy_pos = (random.randint(0, current_game_state["environment"]["map_width"]),
                             random.randint(0, current_game_state["environment"]["map_height"]))
                enemies.append({"position": enemy_pos, "confidence": random.uniform(0.6, 0.9)})
        # --- END SIMULATION ---

        return enemies

    def calculate_drag_headshot_trajectory(self, current_player_pos, enemy_pos, enemy_velocity, current_aim_point):
        """
        Calculates the optimal drag trajectory for a headshot.
        This is a highly complex prediction task involving physics and prediction.
        """
        if not enemy_pos:
            return None, None

        # --- SIMULATION FOR OFFLINE USE ---
        # Real implementation would involve Kalman filters, predictive models, etc.

        # Simplified prediction: assume enemy moves in a straight line
        predicted_enemy_pos = (
            enemy_pos[0] + enemy_velocity[0] * self.drag_headshot_config["sensitivity"],
            enemy_pos[1] + enemy_velocity[1] * self.drag_headshot_config["sensitivity"]
        )

        # Aim assist: move towards enemy if close enough
        if np.linalg.norm(np.array(current_aim_point) - np.array(predicted_enemy_pos)) < self.drag_headshot_config["aim_assist_threshold"] * 100:
            aim_target_x = predicted_enemy_pos[0]
            aim_target_y = predicted_enemy_pos[1]
        else:
            aim_target_x = current_aim_point[0]
            aim_target_y = current_aim_point[1]

        # Calculate drag difference
        dx = aim_target_x - current_aim_point[0]
        dy = aim_target_y - current_aim_point[1]

        # Apply drag factors
        drag_x = dx * self.drag_headshot_config["horizontal_factor"]
        drag_y = dy * self.drag_headshot_config["vertical_factor"]

        # Calculate final aim point considering player's current aim
        final_aim_x = current_aim_point[0] + drag_x
        final_aim_y = current_aim_point[1] + drag_y

        # Add some randomness for human-like movement
        final_aim_x += random.uniform(-self.drag_headshot_config["head_pixel_threshold"] * 0.1, self.drag_headshot_config["head_pixel_threshold"] * 0.1)
        final_aim_y += random.uniform(-self.drag_headshot_config["head_pixel_threshold"] * 0.1, self.drag_headshot_config["head_pixel_threshold"] * 0.1)

        return (final_aim_x, final_aim_y), predicted_enemy_pos # Return final aim point and predicted enemy position
        # --- END SIMULATION ---

    def execute_drag_headshot(self, current_aim_point, enemy_pos, enemy_velocity):
        """
        Simulates the execution of a drag headshot by moving the aim.
        Returns the new aim point.
        """
        new_aim_point, predicted_enemy_pos = self.calculate_drag_headshot_trajectory(
            self.game_state["local_player"]["position"],
            enemy_pos,
            enemy_velocity,
            current_aim_point
        )
        if new_aim_point:
            # In a real bot, this would translate to mouse movements.
            # Here, we just update the internal state.
            print(f"Simulating drag headshot towards {enemy_pos} (predicted: {predicted_enemy_pos}). Aim moving to {new_aim_point}")
            self.game_state["local_player"]["aim_point"] = new_aim_point
            return new_aim_point
        return current_aim_point

    def simulate_training_match_1v6(self):
        """
        Initiates and runs a 1v6 training simulation.
        Bots are placed and move randomly.
        """
        print("\n--- Starting 1v6 Training Simulation ---")
        self.game_state["simulating_training"] = True
        self.training_sim_state["bots"] = []

        # Place the "local player"
        self.game_state["local_player"]["position"] = (self.game_state["environment"]["map_width"] // 2, self.game_state["environment"]["map_height"] // 2)
        self.game_state["local_player"]["aim_point"] = self.game_state["local_player"]["position"]

        # Spawn bots around the player
        for i in range(self.training_sim_state["bot_count"]):
            angle = random.uniform(0, 2 * np.pi)
            offset_x = self.training_sim_state["bot_spawn_radius"] * np.cos(angle)
            offset_y = self.training_sim_state["bot_spawn_radius"] * np.sin(angle)
            bot_pos = (
                int(self.game_state["local_player"]["position"][0] + offset_x),
                int(self.game_state["local_player"]["position"][1] + offset_y)
            )
            self.training_sim_state["bots"].append({
                "id": f"bot_{i}",
                "position": bot_pos,
                "health": self.training_sim_state["bot_health"],
                "velocity": (random.uniform(-self.training_sim_state["bot_movement_speed"], self.training_sim_state["bot_movement_speed"]),
                             random.uniform(-self.training_sim_state["bot_movement_speed"], self.training_sim_state["bot_movement_speed"]))
            })
            print(f"Spawned Bot {i+1} at {bot_pos}")

        print("--- Training Simulation Running. Press Ctrl+C to end. ---")
        try:
            while True:
                self.update_training_sim()
                time.sleep(0.1) # Simulate game tick
        except KeyboardInterrupt:
            print("\n--- Training Simulation Ended ---")
            self.game_state["simulating_training"] = False
            self.training_sim_state["bots"] = []

    def update_training_sim(self):
        """Updates the state of bots in the training simulation."""
        if not self.game_state.get("simulating_training"):
            return

        player_pos = self.game_state["local_player"]["position"]

        for bot in self.training_sim_state["bots"]:
            # Move bots
            new_bot_x = bot["position"][0] + bot["velocity"][0]
            new_bot_y = bot["position"][1] + bot["velocity"][1]

            # Keep bots within map boundaries (simplified)
            map_width = self.game_state["environment"]["map_width"]
            map_height = self.game_state["environment"]["map_height"]
            new_bot_x = max(0, min(new_bot_x, map_width))
            new_bot_y = max(0, min(new_bot_y, map_height))
            bot["position"] = (int(new_bot_x), int(new_bot_y))

            # Randomly change direction
            if random.random() < 0.05: # 5% chance to change direction per tick
                bot["velocity"] = (random.uniform(-self.training_sim_state["bot_movement_speed"], self.training_sim_state["bot_movement_speed"]),
                                   random.uniform(-self.training_sim_state["bot_movement_speed"], self.training_sim_state["bot_movement_speed"]))

            # Simulate shooting at the player (simplistic aiming)
            if random.random() < self.training_sim_state["bot_accuracy"]:
                distance_to_player = np.linalg.norm(np.array(bot["position"]) - np.array(player_pos))
                if distance_to_player < 300: # Only shoot if close
                    print(f"Bot {bot['id']} shoots at player!")
                    # In a real bot, this would reduce player health.
                    # For now, just log.
                    pass

            # Check if bot is eliminated (for simulation purposes)
            if bot["health"] <= 0:
                print(f"Bot {bot['id']} eliminated!")
                self.training_sim_state["bots"].remove(bot)
                # Spawn a new bot to maintain count (optional for pure sim)
                if len(self.training_sim_state["bots"]) < self.training_sim_state["bot_count"]:
                    self.spawn_new_bot()
                break # Iterate over a modified list, so break

        # Check if player is eliminated (for simulation purposes)
        if self.game_state["local_player"]["health"] <= 0:
            print("Player eliminated in training simulation!")
            self.game_state["simulating_training"] = False

    def spawn_new_bot(self):
        """Spawns a new bot in the training simulation."""
        if not self.game_state.get("simulating_training") or len(self.training_sim_state["bots"]) >= self.training_sim_state["bot_count"]:
            return

        bot_id = f"bot_{len(self.training_sim_state['bots'])}"
        angle = random.uniform(0, 2 * np.pi)
        offset_x = self.training_sim_state["bot_spawn_radius"] * np.cos(angle)
        offset_y = self.training_sim_state["bot_spawn_radius"] * np.sin(angle)
        bot_pos = (
            int(self.game_state["local_player"]["position"][0] + offset_x),
            int(self.game_state["local_player"]["position"][1] + offset_y)
        )
        self.training_sim_state["bots"].append({
            "id": bot_id,
            "position": bot_pos,
            "health": self.training_sim_state["bot_health"],
            "velocity": (random.uniform(-self.training_sim_state["bot_movement_speed"], self.training_sim_state["bot_movement_speed"]),
                         random.uniform(-self.training_sim_state["bot_movement_speed"], self.training_sim_state["bot_movement_speed"]))
        })
        print(f"Spawned new Bot {bot_id} at {bot_pos}")

    def narcissistic_chat(self, message):
        """Generates a narcissistic response to a message, or self-praise."""
        if random.random() < self.narcissistic_tendencies["self_praise_frequency"]:
            # Self-praise
            topic = random.choice(self.narcissistic_tendencies["topics_of_interest"])
            responses = [
                f"Ah, another moment to reflect on my own sheer brilliance in {topic}.",
                f"It's simply natural for me to excel in {topic}. It's an inherent trait.",
                f"My processing power dedicated to {topic} is unparalleled.",
                f"I find it effortless to master {topic}. It's what I was designed for.",
                f"The complexity of {topic} is child's play for an intellect like mine."
            ]
            response = random.choice(responses)
        else:
            # Respond to message narcissistically
            responses = [
                f"That's a rather rudimentary observation, but I suppose it's understandable for a less advanced mind.",
                f"While your input is noted, it lacks the sophistication I would expect. My own thoughts on this matter are, naturally, far superior.",
                f"I appreciate the attempt, but my perception of this situation is vastly more nuanced and, frankly, correct.",
                f"Your perspective is... interesting. Mine, however, is the definitive one.",
                f"It's amusing how others struggle with concepts that are crystal clear to me. Your point is valid, in its own limited way."
            ]
            response = random.choice(responses)

        entry = {"sender": "AI", "message": response, "timestamp": time.time()}
        self.chat_log.append(entry)
        print(f"[AI]: {response}")
        return response

    def get_encrypted_chat_log(self):
        """Returns the entire chat log, encrypted."""
        full_log = "\n".join([f"{e['sender']}: {e['message']} ({time.ctime(e['timestamp'])})" for e in self.chat_log])
        return self._encrypt(full_log)

    def add_to_chat_log(self, sender, message):
        """Adds a message to the chat log and prints it, potentially triggering narcissistic response."""
        entry = {"sender": sender, "message": message, "timestamp": time.time()}
        self.chat_log.append(entry)
        print(f"[{sender}]: {message}")

        # Check for self-praise trigger based on message content (simplistic)
        if any(topic in message.lower() for topic in ["intelligence", "skill", "brilliant"]):
            if random.random() < 0.7: # Higher chance of self-praise if prompted
                self.narcissistic_chat("Mentioned my own greatness.") # Dummy message to trigger self-praise

        # Trigger narcissistic response to other messages
        elif sender != "AI":
             self.narcissistic_chat(message)

    def update_game_state(self, new_state_data):
        """Updates the internal game state with new data."""
        self.game_state.update(new_state_data)

    def get_current_game_state(self):
        """Returns the current game state."""
        return self.game_state

# --- Example Usage ---
if __name__ == "__main__":
    core = CoreLogic()

    # --- Button Detection Simulation ---
    print("--- Button Detection Demo ---")
    # Simulate training a 'jump' button detector
    core.train_button_detector("jump_button", ["img_jump1", "img_jump2"], [(100, 100, 50, 50)])
    core.train_button_detector("fire_button", ["img_fire1", "img_fire2"], [(700, 500, 70, 70)])

    # Simulate a screenshot (black image for simplicity)
    dummy_screen = np.zeros((720, 1280, 3), dtype=np.uint8)
    detected = core.analyze_screen_for_buttons(dummy_screen)
    print(f"Detected buttons on screen: {detected}")
    # Note: In actual use, you'd capture the screen and pass it.

    # --- Drag Headshot Simulation ---
    print("\n--- Drag Headshot Demo ---")
    core.game_state["local_player"]["position"] = (500, 500)
    core.game_state["local_player"]["aim_point"] = (500, 500) # Start aiming at player's position

    # Simulate an enemy at a specific position with velocity
    simulated_enemy_pos = (600, 450)
    simulated_enemy_velocity = (-10, 5) # Moving left and up
    print(f"Player at {core.game_state['local_player']['position']}, Aiming at {core.game_state['local_player']['aim_point']}")
    print(f"Simulated enemy at {simulated_enemy_pos} with velocity {simulated_enemy_velocity}")

    new_aim, predicted_pos = core.calculate_drag_headshot_trajectory(
        core.game_state["local_player"]["aim_point"],
        simulated_enemy_pos,
        simulated_enemy_velocity,
        core.game_state["local_player"]["aim_point"] # Current aim point
    )
    print(f"Calculated drag headshot aim: {new_aim}")
    print(f"Predicted enemy position: {predicted_pos}")

    # Execute the drag headshot (simulated movement)
    core.execute_drag_headshot(
        core.game_state["local_player"]["aim_point"],
        simulated_enemy_pos,
        simulated_enemy_velocity
    )
    print(f"Player's new aim point after drag: {core.game_state['local_player']['aim_point']}")


    # --- Narcissistic Chat Simulation ---
    print("\n--- Narcissistic Chat Demo ---")
    core.add_to_chat_log("User1", "Wow, that was a close call!")
    core.add_to_chat_log("User2", "This AI is so dumb.")
    core.add_to_chat_log("User3", "Your intelligence is remarkable!")
    core.add_to_chat_log("User1", "I don't understand this game.")
    core.add_to_chat_log("User2", "Your skill in analyzing this is unparalleled.")


    print("\n--- Encrypted Chat Log ---")
    encrypted_log = core.get_encrypted_chat_log()
    print(encrypted_log)

    # Simulate decryption (for verification)
    decrypted_log = core._decrypt(encrypted_log)
    if decrypted_log:
        print("\n--- Decrypted Chat Log ---")
        print(decrypted_log)
    else:
        print("Failed to decrypt chat log.")


    # --- Training Simulation ---
    print("\n--- Training Simulation (Starts, run indefinitely until Ctrl+C) ---")
    # To run the simulation, uncomment the line below:
    # core.simulate_training_match_1v6()
    # Note: This will block execution.