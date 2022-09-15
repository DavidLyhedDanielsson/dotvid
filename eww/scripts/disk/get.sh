#!/bin/sh

df --output=pcent / | sed '1d;s/^ //;s/%//'