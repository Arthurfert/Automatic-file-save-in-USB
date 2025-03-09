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

for device in drives: # on affiche les infos
    type = win32file.GetDriveType(device)
    info = win32api.GetVolumeInformation(device)
    print("Drive: %s" % device)
    print("Volume: %s" % info[0])
    print(drive_types[type])
    print("-"*72)

os.system('pause')

my_file = Path("D:\.Spotlight-V100\Sync\key.txt") # ! la c'est un test, securite a venir

folderList = [('C:\\Users\\ferta\\Documents\\test','D:\\test'), ('C:\\Users\\ferta\\Documents\\TSE','D:\\TSE'),
            ('C:\\Users\\ferta\\Documents\\PSI','D:\\PSI'), ('C:\\Users\\ferta\\Documents\\Inspire','D:\\INSPIRE')] # liste des dossiers a synchroniser

def list_folders(directory):
    return [f for f in Path(directory).iterdir() if f.is_dir()]

if my_file.is_file(): # si le fichier "key" existe
    print("File exist")
    for folder in folderList: # on synchronise les dossiers
        if list_folders(folder[0]) == []: # si le dossier ne contient pas de dossiers
            if list_folders(folder[1]) == []: # si le dossier ne contient pas de dossiers
                sync(folder[0], folder[1], 'sync', purge=False) # synchronisation des fichiers ordi -> disque
                sync(folder[1], folder[0], 'sync', purge=False) # synchronisation des fichiers disque -> ordi
        else: # si le dossier contient des dossiers
            for subfolder in list_folders(folder[0]): # on synchronise tous les sous-dossiers
                    print('Trying to sync subfolder:', subfolder)
                    sync(subfolder, folder[1]+'\\'+os.path.basename(subfolder), 'sync', purge=False)
                    sync(folder[1]+'\\'+os.path.basename(subfolder), subfolder, 'sync', purge=False)
            for subfolder in list_folders(folder[1]):
                    print('Trying to sync subfolder:', subfolder)
                    sync(subfolder, folder[0]+'\\'+os.path.basename(subfolder), 'sync', purge=False)
                    sync(folder[0]+'\\'+os.path.basename(subfolder), subfolder, 'sync', purge=False)
        print("Sync done in", folder[0], "and", folder[1])

print("Successfully synchronized all folders")
