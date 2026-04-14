# RAGForge
Generatore di una pipeline multimodale di estrazione e normalizzazione contenuti (OCR + ASR + captioning + document parsing + export testuale per ingestion).

INSTALLAZIONE
Si consiglia sempre di creare un ambiente Python dedicato, es. 
python -m venv ragforge
Attivare l'environment (per Windows: ragforge\Scripts\activate)
pip install -r requirements.txt

Bisogna installare il software Tesseract (ATTENTI AD INCLUDERE LA LINGUA ITALIANA), per il riconoscimento OCR, si consiglia di scegliere le lingue italiano ed inglese durante l'istallazione.

Se si hanno problemi col Tkinter, in Windows il pacchetto arriva con l'istallazione di Python (https://www.python.org/)

Lanciare il file install.bat (istalla Tesseract e FFMpeg) - RIAVVIARE IL COMPUTER O APRIRE UN'ALTRA FINESTRA CMD.


