FROM maven:jdk6

EXPOSE 8080

COPY apache* .
RUN tar xf apache* -C /usr/share

COPY tomcat-users.xml /usr/share/apache-*/conf/tomcat-users.xml
COPY docker_tunnels.py /opt/docker_tunnels.py
COPY start-tomcat.sh /opt/start-tomcat.sh
RUN chmod 600 /usr/share/apache-tomcat-*/conf/tomcat-users.xml && \
	chmod +x /opt/docker_tunnels.py && \
	chmod +x /opt/start-tomcat.sh

ENTRYPOINT ["/opt/start-tomcat.sh"]
