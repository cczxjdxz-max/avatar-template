# core_logic.py

import numpy as np
import cv2
import random
import hashlib
import time

class FreeFireAITools:
    def __init__(self):
        self.encryption_key = self._generate_key()
        self.chat_history = []

    def _generate_key(self):
        """Generates a simple, locally stored encryption key."""
        return hashlib.sha256(str(time.time()).encode()).hexdigest()

    def _encrypt_message(self, message):
        """Simple XOR encryption with a generated key."""
        key_bytes = bytes.fromhex(self.encryption_key)
        message_bytes = message.encode()
        encrypted_bytes = bytearray()
        for i in range(len(message_bytes)):
            encrypted_bytes.append(message_bytes[i] ^ key_bytes[i % len(key_bytes)])
        return encrypted_bytes.hex()

    def _decrypt_message(self, encrypted_hex):
        """Simple XOR decryption."""
        key_bytes = bytes.fromhex(self.encryption_key)
        encrypted_bytes = bytes.fromhex(encrypted_hex)
        decrypted_bytes = bytearray()
        for i in range(len(encrypted_bytes)):
            decrypted_bytes.append(encrypted_bytes[i] ^ key_bytes[i % len(key_bytes)])
        return decrypted_bytes.decode()

    def analyze_freefire_buttons(self, screen_capture):
        """
        Analyzes a screen capture to detect Free Fire buttons.
        (Simplified for offline operation: assumes known button templates or color ranges)
        Args:
            screen_capture (np.ndarray): A NumPy array representing the screen capture (BGR format).
        Returns:
            dict: A dictionary with button names and their detected coordinates.
        """
        detected_buttons = {}

        # --- Simplified Button Detection ---
        # In a real scenario, this would involve template matching or object detection models.
        # For offline, we'll simulate finding common buttons based on predefined properties.

        # Example: Detecting a "Shoot" button (e.g., red circular area)
        lower_red = np.array([0, 0, 100])
        upper_red = np.array([50, 50, 255])
        mask_red = cv2.inRange(screen_capture, lower_red, upper_red)
        contours_red, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours_red:
            area = cv2.contourArea(cnt)
            if 500 < area < 5000:  # Arbitrary area for a button
                x, y, w, h = cv2.boundingRect(cnt)
                # Add a slight offset to represent the center if needed
                detected_buttons["shoot"] = (x + w // 2, y + h // 2)
                break # Assume only one primary shoot button for simplicity

        # Example: Detecting a "Jump" button (e.g., blue rectangular area)
        lower_blue = np.array([100, 0, 0])
        upper_blue = np.array([255, 50, 50])
        mask_blue = cv2.inRange(screen_capture, lower_blue, upper_blue)
        contours_blue, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours_blue:
            area = cv2.contourArea(cnt)
            if 400 < area < 4000:
                x, y, w, h = cv2.boundingRect(cnt)
                detected_buttons["jump"] = (x + w // 2, y + h // 2)
                break

        # Add more button detection logic here for other buttons (e.g., crouch, prone, reload)
        # based on their expected color, shape, or pre-saved templates (if available offline).

        return detected_buttons

    def optimize_drag_headshot(self, target_coords, crosshair_coords, screen_width, screen_height):
        """
        Calculates optimal drag distance and angle for a headshot.
        (Simplified for offline: uses basic physics and player prediction)
        Args:
            target_coords (tuple): (x, y) of the enemy's head.
            crosshair_coords (tuple): (x, y) of the player's crosshair.
            screen_width (int): Width of the screen.
            screen_height (int): Height of the screen.
        Returns:
            tuple: (delta_x, delta_y) representing the drag movement.
        """
        # Basic prediction: Assume enemy is moving horizontally
        # In a real scenario, this would involve tracking enemy movement history.
        predicted_target_x = target_coords[0] + random.uniform(-10, 10) # Small random drift
        predicted_target_y = target_coords[1] # Assume stable vertical position for simplicity

        # Calculate distance and angle
        delta_x = predicted_target_x - crosshair_coords[0]
        delta_y = predicted_target_y - crosshair_coords[1]

        # Apply some smoothing/scaling factor (tune these values)
        drag_factor_x = 1.0
        drag_factor_y = 1.2 # Often need to drag more vertically

        final_delta_x = delta_x * drag_factor_x
        final_delta_y = delta_y * drag_factor_y

        # Ensure drag is within reasonable screen bounds (though usually not an issue)
        final_delta_x = max(-screen_width / 2, min(screen_width / 2, final_delta_x))
        final_delta_y = max(-screen_height / 2, min(screen_height / 2, final_delta_y))

        return int(final_delta_x), int(final_delta_y)

    def simulate_training_1v6(self, player_skill_level=0.7):
        """
        Simulates a 1v6 training match.
        (Simplified for offline: random outcomes based on player skill)
        Args:
            player_skill_level (float): A value between 0.0 (low skill) and 1.0 (high skill).
        Returns:
            str: A summary of the simulated match.
        """
        print("\n--- Simulating 1v6 Training Match ---")
        player_kills = 0
        player_deaths = 0
        bot_kills = [0] * 6
        bot_health = [100] * 6 # Assume all bots have full health

        # Simulate rounds or encounters
        for encounter in range(random.randint(10, 20)): # Simulate multiple encounters
            print(f"Encounter {encounter + 1}:")
            active_bots = [i for i, health in enumerate(bot_health) if health > 0]
            if not active_bots:
                print("All bots eliminated. Training simulation complete.")
                break

            # Player action
            player_action_success = random.random() < player_skill_level
            if player_action_success:
                target_bot_index = random.choice(active_bots)
                damage_dealt = random.randint(10, 100) # Damage varies
                bot_health[target_bot_index] -= damage_dealt
                if bot_health[target_bot_index] <= 0:
                    print(f"  Player eliminated Bot {target_bot_index + 1}!")
                    player_kills += 1
                    bot_health[target_bot_index] = 0 # Mark as dead
                else:
                    print(f"  Player hit Bot {target_bot_index + 1} for {damage_dealt} damage.")
            else:
                print("  Player missed or failed action.")

            # Bot actions
            for bot_index in active_bots:
                bot_action_success = random.random() < (0.5 + (1 - player_skill_level) * 0.3) # Bots are slightly easier than player
                if bot_action_success:
                    damage_dealt = random.randint(5, 50)
                    # Simulate player taking damage (simplified)
                    if random.random() < 0.8: # Player doesn't always get hit
                        print(f"  Bot {bot_index + 1} hit Player for {damage_dealt} damage!")
                        player_deaths += 1 # Simplified: any bot hit means a 'death' for training outcome
                        if player_deaths >= 6: # If player "dies" 6 times, simulation ends
                            print("  Player overwhelmed. Training simulation ended.")
                            break
                    else:
                        print(f"  Bot {bot_index + 1} missed Player.")
            if player_deaths >= 6:
                break

            time.sleep(0.1) # Simulate delay between encounters

        print("\n--- Training Simulation Summary ---")
        print(f"Player Kills: {player_kills}")
        print(f"Player Simulated 'Deaths': {player_deaths}")
        remaining_bots = sum(1 for health in bot_health if health > 0)
        print(f"Bots Remaining: {remaining_bots}")
        return f"Simulation complete. Player Kills: {player_kills}, Deaths: {player_deaths}. Bots Remaining: {remaining_bots}"

    def narcissist_chat(self, message):
        """
        Generates a narcissistic response to a user message.
        Args:
            message (str): The user's message.
        Returns:
            str: A narcissistic reply.
        """
        responses = [
            "Oh, you're talking to me? Of course you are. Who wouldn't want to hear my brilliance?",
            "That's an interesting thought, but it would be even better if it came from me.",
            "You're trying to make a point? Fascinating. I've already mastered it.",
            "Yes, I heard you. Though, frankly, my own thoughts are usually more compelling.",
            "I appreciate you sharing that. It's a good starting point for what I'm about to say.",
            "That reminds me, have I told you about my latest incredible achievement? Let me elaborate...",
            "You're asking for my opinion? How predictable. It's always the correct one.",
            "Is that your observation? Mine is far more profound, naturally.",
            "It's adorable you think you've come up with that. I've been contemplating it for ages.",
            "Thank you for the input. It has been duly noted and will be compared against my own superior intellect."
        ]
        reply = random.choice(responses)
        self.chat_history.append({"user": message, "ai": reply})
        return reply

    def get_chat_history(self):
        """
        Retrieves the encrypted chat history.
        Returns:
            list: A list of encrypted chat messages.
        """
        encrypted_history = [self._encrypt_message(f"User: {msg['user']} | AI: {msg['ai']}") for msg in self.chat_history]
        return encrypted_history

    def decrypt_chat_history(self, encrypted_history):
        """
        Decrypts a list of encrypted chat messages.
        Args:
            encrypted_history (list): A list of hex-encoded encrypted messages.
        Returns:
            list: A list of decrypted chat messages.
        """
        decrypted_messages = []
        for encrypted_msg in encrypted_history:
            try:
                decrypted_messages.append(self._decrypt_message(encrypted_msg))
            except Exception as e:
                decrypted_messages.append(f"[Decryption Error: {e}]")
        return decrypted_messages

if __name__ == '__main__':
    # Example Usage
    ai_system = FreeFireAITools()

    print("--- Testing Encryption/Decryption ---")
    original_message = "This is a secret message."
    encrypted = ai_system._encrypt_message(original_message)
    print(f"Original: {original_message}")
    print(f"Encrypted: {encrypted}")
    decrypted = ai_system._decrypt_message(encrypted)
    print(f"Decrypted: {decrypted}")
    print("-" * 30)

    print("--- Testing Narcissist Chat ---")
    print(f"User: Hello there!")
    print(f"AI: {ai_system.narcissist_chat('Hello there!')}")
    print(f"User: What do you think of my idea?")
    print(f"AI: {ai_system.narcissist_chat('What do you think of my idea?')}")
    print(f"User: You are very intelligent.")
    print(f"AI: {ai_system.narcissist_chat('You are very intelligent.')}")

    encrypted_history = ai_system.get_chat_history()
    print("\nEncrypted Chat History:")
    for msg in encrypted_history:
        print(msg)

    decrypted_history = ai_system.decrypt_chat_history(encrypted_history)
    print("\nDecrypted Chat History:")
    for msg in decrypted_history:
        print(msg)
    print("-" * 30)

    print("--- Testing Drag Headshot Calculation ---")
    # Simulate enemy head at (600, 300), crosshair at (500, 350)
    target = (600, 300)
    crosshair = (500, 350)
    screen_w, screen_h = 1280, 720
    drag_move = ai_system.optimize_drag_headshot(target, crosshair, screen_w, screen_h)
    print(f"Target: {target}, Crosshair: {crosshair}")
    print(f"Optimal Drag Movement (dx, dy): {drag_move}")
    print("-" * 30)

    print("--- Testing Training Simulation ---")
    simulation_result = ai_system.simulate_training_1v6(player_skill_level=0.8)
    print(f"\nSimulation Outcome: {simulation_result}")
    print("-" * 30)

    print("--- Testing Button Analysis (Mock Screen) ---")
    # Create a dummy screen capture for button analysis
    mock_screen = np.zeros((720, 1280, 3), dtype=np.uint8)
    # Draw a red circle for shoot button
    cv2.circle(mock_screen, (1100, 600), 40, (0, 0, 255), -1)
    # Draw a blue rectangle for jump button
    cv2.rectangle(mock_screen, (100, 500), (180, 580), (255, 0, 0), -1)

    detected_buttons = ai_system.analyze_freefire_buttons(mock_screen)
    print(f"Detected Buttons: {detected_buttons}")
    print("-" * 30)