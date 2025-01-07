FROM continuumio/miniconda3

WORKDIR /model_training_service

COPY . /model_training_service

# Create volume mount points for persistent data
VOLUME ["/opt/anaconda/envs", \
        "/opt/anaconda/pkgs", \
        "/root/.cache/huggingface", \
        "/model_training_service/mlruns"]

# Mount secrets during build time
RUN --mount=type=secret,id=env_file,target=/model_training_service/.env \
    set -a && . /model_training_service/.env && set +a

# Install dependencies
RUN conda env create -f conda-env.yml

# Make RUN commands use the new environment:
RUN echo "conda activate claim-model-training-env" > ~/.bashrc

ENV PATH="/opt/conda/envs/claim-model-training-env/bin:$PATH"

SHELL ["/bin/bash", "--login", "-c"]

RUN pip --version
    
CMD ["python", "model/model_training.py"]