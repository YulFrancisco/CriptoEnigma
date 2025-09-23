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

    def swap (self, c):
        return self.map.get(c, c)

class EnigmaMachine:
    def __init__(self, rotors, reflector, plugboard=None):
        self.rotors = rotors
        self.reflector = reflector
        self.plugboard = plugboard if plugboard else Plugboard()

    def step_rotors(self):
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
        for r in reversed(self.rotors):
            c = r.encode_forward(c)
        c = self.reflector.reflect(c)
        for r in self.rotors:
            c = r.encode_backward(c)
        c = self.plugboard.swap(c)
        return c

    def process_text(self, text):
        cleaned = "".join([ch.upper() for ch in text if ch.isalpha()])
        out = []
        for ch in cleaned:
            out.append(self.process_character(ch))
        return ''.join(out)

ROTOR_I = "EKMFLGDQVZNTOWYHXUSPAIBRCJ"
ROTOR_II = "AJDKSIRUXBLHWTMCQGZNPYFVOE"
ROTOR_III = "BDFHJLCPRTXVZNYEIWGAKMUSQO"
REFLECTOR_B = "YRUHQSLDPXNGOKMIEBFZCWVJAT"

def make_machine(positions=('A','A','A'), ring_settings=(0,0,0), plug_pairs=None):
    r1 = Rotor(ROTOR_I, notch='Q', position=positions[0], ring_setting=ring_settings[0])
    r2 = Rotor(ROTOR_II, notch='E', position=positions[1], ring_setting=ring_settings[1])
    r3 = Rotor(ROTOR_III, notch='V', position=positions[2], ring_setting=ring_settings[2])
    reflector = Reflector(REFLECTOR_B)
    plug = Plugboard(plug_pairs)
    return EnigmaMachine([r1, r2, r3], reflector, plug)

if __name__ == '__main__':
    machine = make_machine(
        positions=('A','A','A'),
        ring_settings=(0,0,0),
        plug_pairs=[('A','B'), ('C','D')]
    )

    plaintext = input('Plaintext (solo letras): ').strip()
    ciphertext = machine.process_text(plaintext)
    print('Ciphertext', ciphertext)

    machine = make_machine(
        positions=('A','A','A'),
        ring_settings=(0,0,0),
        plug_pairs=[('A', 'B'), ('C','D')]
    )
    decrypted = machine.process_text(ciphertext)
    print('Decrypted: ', decrypted)
