FROM python:3-alpine

# Setup cpu_count monkey patch at python startup
RUN pip install cpu_count \
    && \
    printf "import cpu_count; cpu_count.monkey_patch.setup_monkey_patch()" \
     > "$(find /usr/local/lib/ -type d -name site-packages -print -quit)/cpu_count_monkey_patch.pth"

CMD python -c 'import os; print(os.cpu_count())'
