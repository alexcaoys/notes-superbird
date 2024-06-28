import time
import struct

FORMAT = 'llHHI'
EVENT_SIZE = struct.calcsize(FORMAT)

# Sample code reading input using Python

def main():
    input_event_path = "/dev/input/by-path/platform-rotary@0-event"

    with open(input_event_path, "rb") as f:
        event = f.read(EVENT_SIZE)
        m_key_timer = 0
        
        try:
            while event:
                (_, _, type, code, value) = struct.unpack(FORMAT, event)

                if type != 0 or code != 0 or value != 0:
                    print(f"Event type {type}, code {code}, value {value}")

                event = f.read(EVENT_SIZE)
        except Exception as e:
            print("\nexiting...\n")
            print(e)

if __name__ == "__main__":
    main()