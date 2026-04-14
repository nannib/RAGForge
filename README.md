# RAGForge

[ITALIAN](#ITALIANO)  -  [ENGLISH](#ENGLISH)  

<a name="ITALIANO"></a>  
## ITALIANO
Generatore di una pipeline multimodale di estrazione e normalizzazione contenuti (OCR + ASR + captioning + document parsing + export testuale per ingestion).
Il programma permette di estrarre testi da una directory di input contenente vari tipi di file: docx,pdf,mp4,wav,m4a,jpg,png, ecc..
In una cartella di output sono scritti tutti le parti testuali in file nominati come i file originali ma con estensione TXT.

Il programma inserisce anche la descrizione dei frame di un filmato, la descrizione di un'immagine, la trascrizione audio, ecc..
Una volta che la cartella di output si è popolata, allora si può usarla come directory di RAG, per programmi come open-webui, ecc.ecc..

## INSTALLAZIONE
Si consiglia sempre di creare un ambiente Python dedicato, es. 

python -m venv ragforge

Attivare l'environment (per Windows: ragforge\Scripts\activate)

pip install -r requirements.txt

Lanciare il file install.bat (istalla Tesseract e FFMpeg) - RIAVVIARE IL COMPUTER O APRIRE UN'ALTRA FINESTRA CMD.

Bisogna installare il software Tesseract (ATTENTI AD INCLUDERE LA LINGUA ITALIANA), per il riconoscimento OCR, si consiglia di scegliere le lingue italiano ed inglese durante l'istallazione.

Se si hanno problemi col Tkinter, in Windows il pacchetto arriva con l'istallazione di Python (https://www.python.org/)



# ENGLISH <a id='ENGLISH'></a>
It is a generator of a multimodal content extraction and normalization pipeline (OCR + ASR + captioning + document parsing + text export for ingestion).
The program allows you to extract text from an input directory containing various file types: docx, pdf, mp4, wav, m4a, jpg, png, etc.
All the text parts are written to an output folder in files named like the original files but with a .TXT extension.
The program also inserts the description of the frames of a video, the description of an image, the audio transcript, etc.
Once the output folder is populated, it can be used as a RAG directory for programs like open-webui, etc.

## INSTALLATION
It is always recommended to create a dedicated Python environment, e.g.

python -m venv ragforge

Activate the environment (for Windows: ragforge\Scripts\activate)

pip install -r requirements.txt

Run the install.bat file (installs Tesseract and FFMpeg). RESTART THE COMPUTER OR OPEN ANOTHER CMD WINDOW.

You must install the Tesseract software (BE SURE TO INCLUDE THE ITALIAN LANGUAGE). For OCR recognition, we recommend selecting Italian and English during installation.

If you are having problems with Tkinter, the package comes with the Python installation package for Windows (https://www.python.org/).


