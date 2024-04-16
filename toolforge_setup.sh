#!/usr/bin/env bash

toolforge build start "https://github.com/fastily/mtc-api.git"
toolforge webservice buildservice start --mount=none