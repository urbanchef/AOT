import cx_Oracle
import argparse
import re


class OraMetrics():
    def __init__(self, user, passwd, host, service_name, port):
        self.user = user
        self.passwd = passwd
        self.host = host
        self.service_name = service_name
        self.port = port
        self._dsn = cx_Oracle.makedsn(self.host, self.port, service_name=self.service_name)
        self.connection = cx_Oracle.connect(self.user, self.passwd, self._dsn)


    def wait_class_metrics(self):
        cursor = self.connection.cursor()
        cursor.execute("""
        SELECT inst_info.instance_name,
               inst_info.host_name,
               waitclassstats.wait_class,
               waitclassstats.AAS
          FROM (SELECT inst_id, instance_name, host_name FROM gv$instance) inst_info,
               (SELECT M.INST_ID,
                       n.wait_class,
                       ROUND (m.time_waited / m.INTSIZE_CSEC, 3) AAS
                  FROM gv$waitclassmetric m, gv$system_wait_class n
                 WHERE m.wait_class_id = n.wait_class_id AND n.wait_class != 'Idle'
                UNION
                SELECT inst_id, 'CPU', ROUND (VALUE / 100, 3) AAS
                  FROM gv$sysmetric
                 WHERE metric_name = 'CPU Usage Per Sec' AND GROUP_ID = 2
                UNION
                SELECT aas.inst_id,
                       'CPU_OS',
                       ROUND ( (prcnt.busy * parameter.cpu_count) / 100, 3) - aas.cpu
                  FROM (SELECT inst_id, VALUE busy
                          FROM gv$sysmetric
                         WHERE     metric_name = 'Host CPU Utilization (%)'
                               AND GROUP_ID = 2) prcnt,
                       (SELECT inst_id, VALUE cpu_count
                          FROM gv$parameter
                         WHERE name = 'cpu_count') parameter,
                       (SELECT inst_id, 'CPU', ROUND (VALUE / 100, 3) cpu
                          FROM gv$sysmetric
                         WHERE metric_name = 'CPU Usage Per Sec' AND GROUP_ID = 2)
                       aas
                 WHERE     prcnt.inst_id = parameter.inst_id
                       AND parameter.inst_id = aas.inst_id) waitclassstats
         WHERE waitclassstats.inst_id = inst_info.inst_id
        """)
        for wait in cursor:
            instance_name = wait[0]
            host_name = wait[1]
            wait_name = wait[2]
            wait_value = round(float(wait[3]), 3)
            print("ora_wait_class_metric, host=%s, instance_name=%s, wait_class=%s wait_value=%s" %
                  (host_name, instance_name, re.sub(' ', '_', wait_name), wait_value))


    def wait_event_metrics(self):
        cursor = self.connection.cursor()
        cursor.execute("""
        SELECT inst_info.instance_name,
               inst_info.host_name,
               waitmetrics.wait_class,
               waitmetrics.wait_name,
               waitmetrics.cnt,
               waitmetrics.avgms
          FROM (SELECT m.inst_id,
                       n.wait_class wait_class,
                       n.name wait_name,
                       m.wait_count cnt,
                       ROUND (10 * m.time_waited / NULLIF (m.wait_count, 0), 3) avgms
                  FROM gv$eventmetric m, gv$event_name n
                 WHERE     m.event_id = n.event_id
                       AND n.wait_class <> 'Idle'
                       AND m.wait_count > 0) waitmetrics,
               (SELECT inst_id, instance_name, host_name FROM gv$instance) inst_info
         WHERE inst_info.inst_id = waitmetrics.inst_id
    """)
        for wait in cursor:
            instance_name = wait[0]
            host_name = wait[1]
            wait_class = wait[2]
            wait_name = wait[3]
            wait_cnt = wait[4]
            wait_avgms = wait[5]
            print("ora_wait_event_metric, host=%s, instance_name=%s, wait_class=%s, wait_event=%s count=%s, latency=%s" %
            (host_name, instance_name, re.sub(' ', '_', wait_class), re.sub(' ', '_', wait_name), wait_cnt, wait_avgms))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(conflict_handler='resolve')
    parser.add_argument('-u', '--user', help="Username", required=True)
    parser.add_argument('-w', '--passwd', help="Username password", required=True)
    parser.add_argument('-n', '--hostname', help="Hostname if it is a single instance, scan address if it is a RAC database", required=True)
    parser.add_argument('-p', '--port', required=True)
    parser.add_argument('-s', '--service_name', help="Service name", required=True)

    args = parser.parse_args()

    stats = OraMetrics(args.user, args.passwd, args.hostname, args.service_name, args.port)
    stats.wait_class_metrics()
    stats.wait_event_metrics()