from lib import display, userinput, sdcard
from lib.hydra import config, popup
from machine import Pin, reset
from time import sleep
import os

# os.path.isdir() doesn't work, so using this
def is_dir(dir_path):
    try:
        os.listdir(dir_path)
        print(f"{dir_path} is directory")
        return True
    except:
        print(f"{dir_path} is a file/doesnt exist")
        return False

try:
    if not is_dir("/sd"):
        sdc = sdcard.SDCard()
        sdc.mount()
        mounted_sd = True
    else:
        mounted_sd = True
except:
    mounted_sd = False
    print("could not mount sd")
    
# trying to import libraries
try:
    from .UpyIrTx import UpyIrTx
    from .UpyIrRx import UpyIrRx
    from .NEC2RAW import convert
except:
    try:
        from apps.IR.UpyIrTx import UpyIrTx
        from apps.IR.UpyIrRx import UpyIrRx
        from apps.IR.NEC2RAW import convert
    except:
        if mounted_sd:
            from sd.apps.IR.UpyIrTx import UpyIrTx
            from sd.apps.IR.UpyIrRx import UpyIrRx
            from apps.IR.NEC2RAW import convert
            pass
        else:
            raise

# splits list for correct displaying
def split_list(lst, chunk_size=8, page=0, columns=4):
    result = []
    # Calculate how many items to skip based on the page number
    skip_items = page * (columns * chunk_size - 2)
    # Adjust the list by skipping the first 'skip_items'
    lst = lst[skip_items:]
    if not lst:
        return ["prev_page"]
    # Handle the first list with ["next_page", "prev_page"]
    first_chunk = ["next_page", "prev_page"]
    first_chunk.extend(lst[:chunk_size - 2])
    # Only add the first list if it's not empty (i.e., it has more than just ["next_page", "prev_page"])
    if len(first_chunk) > 2:
        result.append(first_chunk)
    # Handle the next 4 lists of chunk_size
    for i in range(1, columns):
        start_index = (i - 1) * chunk_size - 2 + chunk_size
        chunk = lst[start_index:start_index + chunk_size]
        # Only add non-empty chunks
        if chunk:
            result.append(chunk)
    return result


# reads signals from .ir to json
def load_ir_signals(filename):
    ir_signals = {}
    with open(filename, 'r') as file:
        current_signal = None
        for line in file:
            if line.startswith('name:'):
                current_signal = {'name': line.split(':')[1].strip(), 'data': None}
            elif line.startswith('address:'):
                address = line.split(':')[1].strip()
            elif line.startswith('command:'):
                command = line.split(':')[1].strip()
                converted_signal = convert(address, command)
                print(converted_signal)
                print()
                current_signal['data'] = converted_signal
                ir_signals[current_signal['name']] = current_signal
                del current_signal, address, command
            elif line.startswith('data:'):
                current_signal['data'] = [int(x) for x in line.split(':')[1].strip().split()]
                ir_signals[current_signal['name']] = current_signal
                del current_signal
    file.close()
    return ir_signals
    
#saving
def save_scanned_signal(filename, signal_name, data):
    with open(f"/sd/ir/scanned/{filename}.ir", 'a') as file:
        data_str = ' '.join(map(str, data))
        try:
            temp = file.tell()
        except:
            temp = 0
        if temp == 0:
            file.write("Filetype: IR signals file\nVersion: 1\n# Generated by Cardputer IR app")
        del temp
        file.write(f"\n#\nname: {signal_name}\ntype: raw\nfrequency: 38200\nduty_cycle: 0.330000\ndata: {data_str}")
        
def send_signals(signals_path):
    if mounted_sd:
        with open(f"/sd/latest-ir.txt", 'w') as file:
            file.write(signals_path)
    page = 0
    DISPLAY.fill(CONFIG.palette[2])
    loaded_ir_signals = load_ir_signals(signals_path)  # loads signals
    
    while True:
        DISPLAY.fill(CONFIG.palette[2])
        sig_name = overlay.popup_options(split_list(sorted(loaded_ir_signals), page=page, columns=4))  # asks user which signal to send
        if sig_name is None: # if user presses ESC, exit to main menu
            break
        elif sig_name == "next_page":
            page += 1
        elif sig_name == "prev_page":
            if page > 0:
                page -= 1
        else:
            signal = loaded_ir_signals.get(sig_name)  # find a data from a signal and send it
            if signal:
                tx.send_raw(signal['data'])
    page = 0


# init display
DISPLAY = display.Display()
CONFIG = config.Config()
INPUT = userinput.UserInput()
overlay = popup.UIOverlay()

try:
    tx = UpyIrTx(0, 44)
    page = 0
    if mounted_sd:
        directory_path = "/sd/ir"
    else:
        directory_path = "/ir"
    if not is_dir(directory_path):
        os.mkdir(directory_path)
        
    choice_list = ["Load file", "Scan remote", "Exit"]
    if mounted_sd:
        choice_list.insert(0, "Load last")
    
    while True:  # main loop
        # main menu
        DISPLAY.fill(CONFIG.palette[2])
        user_choice = overlay.popup_options(choice_list, title=f"InfraRed")
        if user_choice == "Load last":
            try:
                with open("/sd/latest-ir.txt", "r") as file:
                    last_signals_path = file.read()
                send_signals(last_signals_path)
            except:
                user_choice == "Load file"
        if user_choice == "Load file":
            DISPLAY.fill(CONFIG.palette[2])
            selected_path = overlay.popup_options(split_list(lst = os.listdir(directory_path) + [".."], page=page, columns=2))  # ls
            if selected_path is None: #  if user presses ESC, return to previous dir
                directory_path = "/".join(list(directory_path.split('/')[0:-1]))
            elif selected_path == "next_page":
                page += 1
                # implement later
            elif selected_path == "prev_page":
                if page > 0:
                    page -= 1
                # implement later
            elif is_dir(f"{directory_path}/{selected_path}"):  # if user tries to open a directory, enter it
                directory_path = directory_path + '/' + selected_path
                page = 0
            
            elif selected_path.endswith('.ir'):
                send_signals(f"{directory_path}/{selected_path}")
            else:
                overlay.popup("Only .ir can be opened here")

        elif user_choice == "Scan remote":
            DISPLAY.fill(CONFIG.palette[2])
            overlay.popup("Connent IR reciever module to groove. Press enter when ready")
            DISPLAY.fill(CONFIG.palette[2])
            IR_RX_PIN = overlay.popup_options(['1', '2'], title="Select pin")
            rx = UpyIrRx(Pin(int(IR_RX_PIN), Pin.IN))
            DISPLAY.fill(CONFIG.palette[2])
            scan_filename = overlay.text_entry(title="Filename to write")
            
            while True:
                overlay.draw_textbox("Scanning, press BtnRst to exit", 120, 62, padding=8)
                DISPLAY.show()
                rx.record(wait_ms=2000)  # listens at IR_RX_PIN for signals
                if rx.get_mode() == UpyIrRx.MODE_DONE_OK:
                    DISPLAY.fill(CONFIG.palette[2])
                    scan_name = overlay.text_entry(title="Enter signal name")
                    if scan_name == '':  # exit to main menu if empty name
                        break
                    DISPLAY.fill(CONFIG.palette[2])
                    signal_list = rx.get_record_list()  # get data of signal
                    save_scanned_signal(scan_filename, scan_name, signal_list)
            
            del rx, IR_RX_PIN, scan_filename, scan_name, signal_list  # cleanup
                
        elif user_choice == "Exit":
            reset()
        
        sleep(0.1)

except Exception as e:  # for debugging
    overlay.error(str(e))
    raise # error will be logged in `log.txt`
