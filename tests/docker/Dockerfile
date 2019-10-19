FROM python:3-alpine

# Setup cpu_count monkey patch at python startup
RUN pip install cpu_count \
    && \
    printf "\nimport cpu_count\ncpu_count.monkey_patch.setup_monkey_patch()\n" \
     >> "$(find /usr/local/lib/ -type d -name site-packages -print -quit)/sitecustomize.py"

CMD python -c 'import os; print(os.cpu_count())'
