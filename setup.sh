#!/bin/bash

# zsh uses compinstall
# config files:
# - .zshrc

DOTVID=~/.config/dotvid
mkdir -p $DOTVID

yay --noconfirm -Ss git zsh oh-my-zsh-git fzf ack nvim ripgrep htop tree alacritty flameshot clight polybar ttf-iosevka-nerd

# i3
## symlinks
mkdir -p ~/.config/i3 && ln -s -f $DOTVID/i3/config ~/.config/i3/config

# ZSH and oh-my-zsh
## install
chsh /usr/bin/zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
## config
ZSH_CUSTOM=$DOTVID/oh-my-zsh-custom
mkdir -p $ZSH_CUSTOM
mkdir -p $ZSH_CUSTOM/themes

git clone https://github.com/jeffreytse/zsh-vi-mode $ZSH_CUSTOM/plugins/zsh-vi-mode
curl -L https://raw.githubusercontent.com/sbugzu/gruvbox-zsh/master/gruvbox.zsh-theme > $ZSH_CUSTOM/themes/gruvbox.zsh-theme
##symlinks
ln -s -f $DOTVID/.zshrc ~/.zshrc

# nvim
## symlinks
mkdir -p ~/.config/nvim && ln -s -f $DOTVID/nvim/init.vim ~/.config/nvim/init.vim

# alacritty
## symlinks
mkdir -p ~/.config/alacritty && ln -s -f $DOTVID/alacritty/alacritty.yml ~/.config/alacritty/alacritty.yml
