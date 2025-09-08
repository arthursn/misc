FROM gcc:latest

RUN apt update && apt install -y \
    sudo \
    cmake \
    gdb \
    valgrind \
    vim \
    zsh \
    && rm -rf /var/lib/apt/lists/*

ARG USERNAME=$USERNAME
ARG USER_UID=$USER_UID
ARG USER_GID=$USER_GID

# Create the user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

USER $USERNAME

# Setup oh-my-zsh
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
RUN sed -i 's/^ZSH_THEME=".*"/ZSH_THEME="af-magic"/' ~/.zshrc