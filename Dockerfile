from brunneis/python:3.9
RUN pip install requests lxml pyyaml
COPY commenter.py entrypoint.sh /
ENTRYPOINT /entrypoint.sh
