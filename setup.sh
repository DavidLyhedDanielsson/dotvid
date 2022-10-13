#!/bin/bash
set -e

type=$(loginctl show-session $(loginctl | grep $(whoami) | awk '{print $1}') -p Type)
using_wayland=true
if [ $type = "Type=x11" ]; then
    using_wayland=false
    echo "Installing i3 stuff"
fi

# https://forum.endeavouros.com/t/faq-issues-with-signature-is-marginal-trust-signature-is-unknown-trust-or-invalid-or-corrupted-package/6756

# zsh uses compinstall
# config files:
# - .zshrc

DOTVID=~/.config/dotvid
mkdir -p $DOTVID

# Update first !
# yay --noconfirm

yay --noconfirm -S git zsh oh-my-zsh-git fzf ack neovim ripgrep htop tree alacritty flameshot clight ttf-iosevka-nerd  pamixer acpi jq discord
pip install pulsectl psutil

if [ "$using_wayland" = true ] ; then
    yay --noconfirm -S eww-wayland-git wl-clipboard swaybg
else
    yay --noconfirm -S eww 
fi

safe_create() {
    if [ -d "$1" ]; then
        mv $1 "$1_old"
        mkdir $1
    else
        mkdir -p $1
    fi
}

# i3 X11
## symlinks
if [ "$using_wayland" = false ] ; then
    safe_create ~/.config/i3
    ln -s -f $DOTVID/i3/config ~/.config/i3/config
fi

# ZSH and oh-my-zsh
## install
chsh -s /usr/bin/zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
## config
ZSH_CUSTOM=$DOTVID/oh-my-zsh-custom
safe_create $ZSH_CUSTOM
mkdir -p $ZSH_CUSTOM/themes

git clone https://github.com/jeffreytse/zsh-vi-mode $ZSH_CUSTOM/plugins/zsh-vi-mode
curl -L https://raw.githubusercontent.com/sbugzu/gruvbox-zsh/master/gruvbox.zsh-theme > $ZSH_CUSTOM/themes/gruvbox.zsh-theme
##symlinks
ln -s -f $DOTVID/.zshrc ~/.zshrc

# nvim
## symlinks
safe_create ~/.config/nvim
ln -s -f $DOTVID/nvim/init.vim ~/.config/nvim/init.vim

# alacritty
## symlinks
safe_create ~/.config/alacritty
ln -s -f $DOTVID/alacritty/alacritty.yml ~/.config/alacritty/alacritty.yml

# eww
## symlinks
if [ -d "~/.config/eww" ]; then
    mv "~/.config/eww_old"
fi
ln -s -f $DOTVID/eww ~/.config/eww


if [ "$using_wayland" = true ] ; then
    # hypr
    ## symlinks
    if [ -d "~/.config/hypr" ]; then
        mv "~/.config/hypr_old"
    fi
    ln -s -f $DOTVID/hypr ~/.config/hypr
fi

# git
git config --global user.email "davidlyheddanielsson@gmail.com"
git config --global user.name "David Lyhed Danielsson"

if [ "$using_wayland" = false ] ; then
    # autorandr
    ## symlinks
    safe_create ~/.config/autorandr
    ln -s -f $DOTVID/autorandr/postswitch ~/.config/autorandr/postswitch
fi
