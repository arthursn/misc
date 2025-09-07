FROM gcc:latest

RUN apt update && apt install -y \
    cmake \
    gdb \
    valgrind \
    vim \
    zsh \
    && rm -rf /var/lib/apt/lists/*

RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

RUN sed -i 's/^ZSH_THEME=".*"/ZSH_THEME="af-magic"/' ~/.zshrc

WORKDIR /workspace