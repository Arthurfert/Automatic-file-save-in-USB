import os
import win32api
import win32file
from pathlib import Path
from dirsync import sync

os.system("cls")
drive_types = { # liste des types de disques
                win32file.DRIVE_UNKNOWN : "Unknown\n   Drive type can't be determined.",
                win32file.DRIVE_REMOVABLE : "Removable\n   Drive has removable media. This includes all floppy drives and many other varieties of storage devices.",
                win32file.DRIVE_FIXED : "Fixed\n   Drive has fixed (nonremovable) media. This includes all hard drives, including hard drives that are removable.",
                win32file.DRIVE_REMOTE : "Remote\n   Network drives. This includes drives shared anywhere on a network.",
                win32file.DRIVE_CDROM : "CDROM\n   Drive is a CD-ROM. No distinction is made between read-only and read/write CD-ROM drives.",
                win32file.DRIVE_RAMDISK : "RAMDisk\n   Drive is a block of random access memory (RAM) on the local computer that behaves like a disk drive.",
                win32file.DRIVE_NO_ROOT_DIR : "The root directory does not exist."
            }

drives = win32api.GetLogicalDriveStrings().split('\x00')[:-1] # obtention liste des disques de l'ordinateur

removable_drives = [device for device in drives if win32file.GetDriveType(device) == win32file.DRIVE_REMOVABLE]

print("This computer has the following drives:")
print("-"*72)
for device in drives: # on affiche les infos
    type = win32file.GetDriveType(device)
    info = win32api.GetVolumeInformation(device)
    print("Drive: %s" % device)
    print("Drive Name: %s" % info[0])
    print(drive_types[type])
    print("-"*72)

os.system('pause')

folderList = [('C:\\Users\\ferta\\Documents\\TSE','D:\\TSE'), ('C:\\Users\\ferta\\Documents\\PSI','D:\\PSI'),
            ('C:\\Users\\ferta\\Documents\\Inspire','D:\\Inspire')] # liste des dossiers a synchroniser

def list_folders(directory):
    return [f for f in Path(directory).iterdir() if f.is_dir()]

def sync_folders(src, dst):
    try:
        sync(src, dst, 'sync', purge=False)
        sync(dst, src, 'sync', purge=False)
        for subfolder in list_folders(src):
            sync_folders(subfolder, Path(dst) / subfolder.name)
        for subfolder in list_folders(dst):
            sync_folders(subfolder, Path(src) / subfolder.name)
    except Exception as e:
        print(f"Error syncing {src} and {dst}: {e}")

try:
    for device in removable_drives:
        if Path(device + "\\Sync\\key.txt").is_file(): # si le fichier "key" existe # ! la c'est un test, sécurité a venir
            print("File exist in", device, win32api.GetVolumeInformation(device)[0])
            for folder in folderList: # on synchronise les dossiers
                sync_folders(folder[0], folder[1])
                print("Sync done in", folder[0], "and", folder[1])
            print("Successfully synchronized all folders")
        else:
            print("Key doesn't exist or couldn't be found")
        os.system('pause')
        print("-"*72)
    print("Sync completed in all valid drives")
except Exception as e:
    print(f"Error: {e}")
    print("-"*72)