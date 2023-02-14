FROM python:3.8
#Define dependencies and Bash shell
ENV DEBIAN_FRONTEND noninteractive

WORKDIR  /home

RUN apt-get update -qq ; apt-get upgrade ; \
    apt-get install -y gridengine-client git ; \
    apt-get install -y build-essential tar curl ; \
    apt-get autoremove -y && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

#RUN chsh -s /bin/bash
#SHELL ["/bin/bash", "-c"]
#RUN source venv/bin/activate
RUN pwd

#Install python and other dependencies for the Tool

RUN apt-get update ; apt-get upgrade ; \
    apt-get install -y python3-pip python-dev build-essential; \
    apt-get autoremove -y && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

#RUN update-alternatives --set python /usr/bin/python3.7
#RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1

RUN python3 --version
RUN pip3 install --upgrade pip

RUN pip3 install nibabel SimpleITK trimesh asttokens==2.2.1 backcall==0.2.0 biobb-analysis==3.8.0 biobb-common==3.8.1 biobb-gromacs==3.8.0 biobb-io==3.8.0 biobb-model==3.8.0 biopython==1.79 comm==0.1.2 contourpy==1.0.7 cycler==0.11.0 debugpy==1.6.5 ipykernel==6.20.2 ipython==8.8.0 kiwisolver==1.4.4 pandas==1.5.3 opencv-python==4.5.1.48
    
RUN pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu
RUN pip3 install "git+https://github.com/facebookresearch/pytorch3d.git"

#Define VRE tool download 
WORKDIR /home
RUN git clone --branch main https://github.com/mapoferri/vre_app_3dshaper.git
RUN pwd
RUN cd /home/vre_app_3dshaper
WORKDIR /home/vre_app_3dshaper
COPY ./inp1 /home/vre_app_3dshaper/inp1
COPY ./inp2 /home/vre_app_3dshaper/inp2

RUN ls

#RUN conda env create -f environment.yml 
#RUN conda activate biobb_guild
#COPY disc4all-data/ /home/vre_app_3dshaper/disc4all-data/
#COPY datasets/ /home/vre_app_3dshaper/datasets/

COPY ~/.ssh /root/.ssh


RUN pip3 install --upgrade wheel
RUN pip3 install -r requirements.txt
RUN python /home/vre_app_3dshaper/setup.py build
RUN python /home/vre_app_3dshaper/setup.py install


#RUN python /home/vre_app_guild/biobb_guild build
RUN pip3 install --upgrade wheel
RUN pip3 install -r requirements.txt
#RUN python /home/vre_app_guild/biobb_guild install

RUN ls

CMD ./VRE_RUNNER --config tests/basic/config.json --in_metadata tests/basic/in_metadata.json --out_metadata out_metadata.json --log_file VRE_RUNNER.log
