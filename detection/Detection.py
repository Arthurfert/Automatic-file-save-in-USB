import os
import sys
import win32api
import win32file
import subprocess
from pathlib import Path

# Ajouter le répertoire parent au sys.path pour pouvoir importer logger
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger.logger import logger

# TODO : ajouter un systeme de clé pour la synchronisation
# TODO : ajouter un systeme de log
# TODO : ajouter un systeme de configuration
# TODO : ajouter une interface graphique ?

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

# Liste des dossiers source à synchroniser (sur l'ordinateur)
folders_to_sync = ['TSE', 'PSI', 'Inspire']
base_path = 'C:\\Users\\ferta\\Documents'

def get_folder_pairs(usb_drive):
    """
    Génère dynamiquement les paires de dossiers à synchroniser en fonction du lecteur USB détecté.
    
    Args:
        usb_drive: Lettre du lecteur USB (ex: 'E:\\')
    
    Returns:
        Liste de tuples (chemin_source, chemin_destination)
    """
    return [(f'{base_path}\\{folder}', f'{usb_drive}{folder}') for folder in folders_to_sync]

def list_folders(directory):
    return [f for f in Path(directory).iterdir() if f.is_dir()]

def sync_folders_robocopy(src, dst):
    """
    Synchronise deux dossiers en utilisant robocopy de manière bidirectionnelle.
    Copie uniquement les fichiers plus récents ou manquants, sans supprimer.
    
    /E : Copie les sous-dossiers, y compris les vides
    /DCOPY:DAT : Copie les attributs de dossier (Date, Attributes, Timestamps)
    /COPY:DAT : Copie les attributs de fichier (Date, Attributes, Timestamps)
    /R:1 : 1 tentative en cas d'échec
    /W:1 : 1 seconde d'attente entre les tentatives
    /MT:8 : Utilise 8 threads pour la copie (plus rapide)
    /XN : eXclude Newer - copie si source est plus récent ou identique (ignore si destination plus récente)
    /FFT : Assume FAT File Times (2 secondes de précision) - important pour USB
    /V : Verbose pour voir ce qui est copié
    """
    try:
        # Créer les dossiers s'ils n'existent pas
        Path(src).mkdir(parents=True, exist_ok=True)
        Path(dst).mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Synchronisation de {src} <-> {dst}")
        
        # De src vers dst : copie les fichiers plus récents ou manquants de src vers dst
        cmd_src_to_dst = [
            'robocopy',
            str(src),
            str(dst),
            '/E',           # Copie les sous-dossiers
            '/DCOPY:DAT',   # Copie les attributs de dossier
            '/COPY:DAT',    # Copie les attributs de fichier
            '/R:1',         # 1 tentative en cas d'échec
            '/W:1',         # 1 seconde d'attente
            '/MT:8',        # 8 threads
            '/XN',          # eXclut les fichiers Newer dans destination (copie si src >= dst)
            '/FFT'          # Assume FAT File Times (important pour clés USB)
        ]
        
        # De dst vers src : copie les fichiers plus récents ou manquants de dst vers src
        cmd_dst_to_src = [
            'robocopy',
            str(dst),
            str(src),
            '/E',
            '/DCOPY:DAT',
            '/COPY:DAT',
            '/R:1',
            '/W:1',
            '/MT:8',
            '/XN',          # eXclut les fichiers Newer dans destination (copie si dst >= src)
            '/FFT'          # Assume FAT File Times
        ]
        
        # Exécuter robocopy (codes de retour 0-7 sont considérés comme succès)
        logger.info(f"Copie {src} -> {dst}...")
        result1 = subprocess.run(cmd_src_to_dst, capture_output=True, text=True, encoding='cp850')
        
        logger.info(f"Copie {dst} -> {src}...")
        result2 = subprocess.run(cmd_dst_to_src, capture_output=True, text=True, encoding='cp850')
        
        # Afficher les résultats détaillés
        if result1.returncode <= 7:
            logger.info(f"✓ Copie {src} -> {dst} terminée (code: {result1.returncode})")
            # Afficher la sortie complète pour debug
            if result1.stdout:
                logger.info("--- Détails de la synchronisation ---")
                for line in result1.stdout.split('\n'):
                    line = line.strip()
                    if line and ('Fichiers' in line or 'Dossiers' in line or 'Files' in line or 'Dirs' in line or 
                                 'Total' in line or 'Copié' in line or 'Copied' in line or 'Nouveau' in line or 'New' in line):
                        logger.info(f"  {line}")
        else:
            logger.error(f"Erreur robocopy {src} -> {dst} (code: {result1.returncode})")
            logger.error(result1.stderr if result1.stderr else result1.stdout)
        
        if result2.returncode <= 7:
            logger.info(f"✓ Copie {dst} -> {src} terminée (code: {result2.returncode})")
            if result2.stdout:
                logger.info("--- Détails de la synchronisation ---")
                for line in result2.stdout.split('\n'):
                    line = line.strip()
                    if line and ('Fichiers' in line or 'Dossiers' in line or 'Files' in line or 'Dirs' in line or 
                                 'Total' in line or 'Copié' in line or 'Copied' in line or 'Nouveau' in line or 'New' in line):
                        logger.info(f"  {line}")
        else:
            logger.error(f"Erreur robocopy {dst} -> {src} (code: {result2.returncode})")
            logger.error(result2.stderr if result2.stderr else result2.stdout)
            
    except Exception as e:
        logger.error(f"Erreur lors de la synchronisation {src} <-> {dst}: {e}")

try:
    for device in removable_drives:
        if Path(device + "\\Sync\\key.txt").is_file(): # si le fichier "key" existe # ! la c'est un test, sécurité a venir
            logger.info(f"File exist in {device} {win32api.GetVolumeInformation(device)[0]}")
            
            # Générer dynamiquement les paires de dossiers pour ce lecteur USB
            folderList = get_folder_pairs(device)
            logger.info(f"Synchronisation avec le lecteur {device}")
            
            for folder in folderList: # on synchronise les dossiers
                sync_folders_robocopy(folder[0], folder[1])
                logger.info(f"Sync done in {folder[0]} and {folder[1]}")
            logger.info("Successfully synchronized all folders")
        else:
            logger.warning("Key doesn't exist or couldn't be found")
        os.system('pause')
        print("-"*72)
    logger.info("Sync completed in all valid drives")
except Exception as e:
    logger.error(f"Error: {e}")
    print("-"*72)