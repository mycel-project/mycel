#!/usr/bin/env bash
case "$1" in
  setup)  bash scripts/setup.sh ;;
  run)    bash scripts/run.sh ;;
  update) bash scripts/update.sh ;;
  *) echo "Usage: ./mycel.sh {setup|run|update}" ;;
esac
