FROM ubuntu:18.04
RUN apt-get update -y
RUN apt-get install gcc g++ cmake git sudo libssl-dev zlib1g-dev -y mysql-server mysql-client libmysqlclient-dev && apt-get clean -y
RUN git clone -b poco-1.11.1 https://github.com/pocoproject/poco.git && cd poco && mkdir cmake-build && cd cmake-build && cmake .. && cmake --build . --config Release && cmake --build . --target install && cd .. && rm -r /poco/*
RUN git clone  https://github.com/DVDemon/hl_mai_04_sql.git && cd hl_mai_04_sql && mkdir CMakeFiles && cd CMakeFiles && cmake .. && cmake --build . --config Release && cd /
ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
WORKDIR /hl_mai_04_sql/CMakeFiles
ENTRYPOINT [ "./sql_test" ]
CMD ["localhost"]