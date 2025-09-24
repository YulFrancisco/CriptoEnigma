from collections import Counter

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

class Rotor:
    def __init__(self, wiring, notch, position='A', ring_setting=0):
        self.wiring = wiring
        self.notch = notch
        self.position = ALPHABET.index(position.upper())
        self.ring_setting = ring_setting

    def step(self):
        self.position = (self.position + 1) % 26

    def at_notch(self):
        return ALPHABET[self.position] in self.notch

    def encode_forward(self, c):
        idx = (ALPHABET.index(c) + self.position - self.ring_setting) % 26
        wired = self.wiring[idx]
        out = ALPHABET[(ALPHABET.index(wired) - self.position + self.ring_setting) % 26]
        return out

    def encode_backward(self, c):
        idx = (ALPHABET.index(c) + self.position - self.ring_setting) % 26
        wired_index = self.wiring.index(ALPHABET[idx])
        out = ALPHABET[(wired_index - self.position + self.ring_setting) % 26]
        return out

class Reflector:
    def __init__(self, wiring):
        self.wiring = wiring

    def reflect(self, c):
        idx = ALPHABET.index(c)
        return self.wiring[idx]

class Plugboard:
    def __init__(self, pairs=None):
        self.map = {c: c for c in ALPHABET}
        if pairs:
            for a, b in pairs:
                a, b = a.upper(), b.upper()
                self.map[a] = b
                self.map[b] = a

    def swap(self, c):
        return self.map.get(c, c)

class EnigmaMachine:
    def __init__(self, rotors, reflector, plugboard=None):
        # rotors: [left, middle, right]
        self.rotors = rotors
        self.reflector = reflector
        self.plugboard = plugboard if plugboard else Plugboard()

    def step_rotors(self):
        # stepping with double-step behavior
        right = self.rotors[2]
        middle = self.rotors[1]
        left = self.rotors[0]

        if middle.at_notch():
            middle.step()
            left.step()
        if right.at_notch():
            middle.step()
            right.step()

    def process_character(self, ch):
        if ch not in ALPHABET:
            return ch
        self.step_rotors()
        c = self.plugboard.swap(ch)
        for r in reversed(self.rotors):  # right -> left
            c = r.encode_forward(c)
            c = self.reflector.reflect(c)
        for r in self.rotors:  # left -> right (backwards)
            c = r.encode_backward(c)
            c = self.plugboard.swap(c)
        return c

    def process_text(self, text):
        cleaned = "".join([ch.upper() for ch in text if ch.isalpha()])
        out = []
        for ch in cleaned:
            out.append(self.process_character(ch))
        return ''.join(out)

# Historical wirings (rotors I, II, III and Reflector B)
ROTOR_I = "EKMFLGDQVZNTOWYHXUSPAIBRCJ"
ROTOR_II = "AJDKSIRUXBLHWTMCQGZNPYFVOE"
ROTOR_III = "BDFHJLCPRTXVZNYEIWGAKMUSQO"
REFLECTOR_B = "YRUHQSLDPXNGOKMIEBFZCWVJAT"

def make_machine(positions=('A', 'A', 'A'), ring_settings=(0, 0, 0), plug_pairs=None):
    r1 = Rotor(ROTOR_I, notch='Q', position=positions[0], ring_setting=ring_settings[0])
    r2 = Rotor(ROTOR_II, notch='E', position=positions[1], ring_setting=ring_settings[1])
    r3 = Rotor(ROTOR_III, notch='V', position=positions[2], ring_setting=ring_settings[2])
    reflector = Reflector(REFLECTOR_B)
    plug = Plugboard(plug_pairs)
    return EnigmaMachine([r1, r2, r3], reflector, plug)

# -----------------------
# Attack parameters
# -----------------------
ciphertext = "ILACBBMTBE"  # ciphertext to attack (example)
# English letter frequency (percentage-like values)
expected_freq = {
    'E': 12.0, 'T': 9.10, 'A': 8.12, 'O': 7.68, 'I': 7.31, 'N': 6.95,
    'S': 6.28, 'R': 6.02, 'H': 5.92, 'L': 4.02, 'D': 4.32, 'C': 2.71,
    'U': 2.88, 'M': 2.61, 'F': 2.30, 'Y': 2.11, 'W': 2.09, 'G': 2.03,
    'P': 1.82, 'B': 1.49, 'V': 1.11, 'K': 0.69, 'X': 0.17, 'Q': 0.11, 'J': 0.10, 'Z': 0.07
}
# normalize expected frequencies to sum=1
total = sum(expected_freq.values())
for k in expected_freq:
    expected_freq[k] = expected_freq[k] / total

def chi_squared_score(text):
    N = len(text)
    counts = Counter(text)
    score = 0.0
    for ch in ALPHABET:
        observed = counts.get(ch, 0)
        expected = expected_freq[ch] * N
        # if expected is zero it would be an issue, but expected_freq uses english stats so none zero
        score += (observed - expected) ** 2 / expected
    return score

# Brute-force all 26^3 rotor starting positions, assume known rotor order and no plugboard
results = []
for p1 in ALPHABET:
    for p2 in ALPHABET:
        for p3 in ALPHABET:
            machine = make_machine(positions=(p1, p2, p3), ring_settings=(0, 0, 0), plug_pairs=None)
            plain_candidate = machine.process_text(ciphertext)
            score = chi_squared_score(plain_candidate)
            results.append((score, (p1, p2, p3), plain_candidate))

# sort best (lowest chi-square)
results.sort(key=lambda x: x[0])
top5 = results[:5]

print("Top 5 candidates (chi-squared scoring):\n")
for sc, pos, txt in top5:
    print(f"Positions: {pos} | Score: {sc:.2f} | Plain: {txt}")

# check if a known expected plaintext appears (optional)
target = "HELLOWORLD"
found = [r for r in results if r[2] == target]
print("\nEvidence check: '{}' found in results? -> {}".format(target, "YES" if found else "NO"))
if found:
    for sc, pos, txt in found:
        print("Found at positions", pos, "with score", sc)