# Data labelling

We are following this [colab](https://colab.research.google.com/github/EdjeElectronics/Train-and-Deploy-YOLO-Models/blob/main/Train_YOLO_Models.ipynb#scrollTo=cfaWho47RGDf) and [youtube](https://www.youtube.com/watch?v=r0RspiLG260) tutorials.

https://www.youtube.com/watch?v=r0RspiLG260

## How we will label our dataset

We will use the label studio python package https://labelstud.io/


run the following command to activate the python venv and to install label-studio

```sh 
.\venv\Scripts\activate 

pip install -U label-studio
```

Before running label studio just be sure to enable local file storage with the following command in the terminal

```sh
export LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true
```

If you are on windows the command is the following.

```sh
set LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true
```


This one is the one to run.
```sh 
label-studio
```


