def hex_to_bin(hex_value, bits=32):
    """Convert a hex value to a binary string with a fixed number of bits."""
    bin_value = bin(int(hex_value, 16))[2:]  # Convert to binary and strip the '0b'
    return pad_binary_string(bin_value, bits)

def pad_binary_string(bin_value, bits):
    """Pad a binary string with leading zeros to ensure it has the specified number of bits."""
    if len(bin_value) < bits:
        return '0' * (bits - len(bin_value)) + bin_value
    return bin_value

def generate_raw_timing(binary_string):
    """Convert binary string to raw timing list based on NEC protocol."""
    timing = []
    for bit in binary_string:
        if bit == '1':
            timing.extend([560, 1690])
        else:
            timing.extend([560, 560])
    return timing

def nec_ir_signal(address, command):
    """Convert NEC IR signal address and command to raw timing format."""
    # Convert address and command to binary strings
    address = address.replace(" ", "")
    command = command.replace(" ", "")
    address_bin = hex_to_bin(address)
    address_inv_bin = hex_to_bin(hex(int(address, 16) ^ 0xFFFFFFFF))[2:]
    address_inv_bin = pad_binary_string(address_inv_bin, 32)
    command_bin = hex_to_bin(command)
    command_inv_bin = hex_to_bin(hex(int(command, 16) ^ 0xFFFFFFFF))[2:]
    command_inv_bin = pad_binary_string(command_inv_bin, 32)

    # Start of transmission (header)
    raw_signal = [9000, 4500]

    # Append address and inverted address timings
    raw_signal += generate_raw_timing(address_bin)
    raw_signal += generate_raw_timing(address_inv_bin)

    # Append command and inverted command timings
    raw_signal += generate_raw_timing(command_bin)
    raw_signal += generate_raw_timing(command_inv_bin)

    # Stop bit
    raw_signal.append(560)

    return raw_signal

def format_raw_timing(raw_signal):
    """Format raw timing list into a string for display."""
    return ' '.join(map(str, raw_signal))

def convert(address, command):
    return nec_ir_signal(address, command)

if __name__ == "__main__":
    
    examples = [
    {'name': 'POWER', 'address': '81 66 00 00', 'command': '817E0000'},
    {'name': 'TEMP-', 'address': '81660000', 'command': '8A750000'},
    {'name': 'TEMP+', 'address': '81660000', 'command': '857A0000'},
    {'name': 'Fan Speed', 'address': '81660000', 'command': '99660000'},
    {'name': 'Timer', 'address': '81660000', 'command': '9F600000'},
    {'name': 'MODE', 'address': '81660000', 'command': '9B640000'}
    ]
    
    for example in examples:
        print(convert(example["address"], example["command"]))
