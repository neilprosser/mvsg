import commands
import httplib
import json
import sys
import time

if len(sys.argv) != 7:
    sys.stderr.write('Not enough (or too many) arguments\n')
    sys.exit(1)

hostname = sys.argv[1].partition('.')[0].lower()
environment = sys.argv[2].lower()
application = sys.argv[3].lower()
prefix = '{0}.{1}.{2}'.format(environment, application, hostname)

host = sys.argv[4]
port = sys.argv[5]
omit_jvm_stats = sys.argv[6].lower() == 'true'

timestamp_millis = int(round(time.time() * 1000))
timestamp = timestamp_millis / 1000
connection = httplib.HTTPConnection(host, port, timeout = 5)

def tidy_up():
    connection.close()

def request_and_response_or_bail(method, url, message):
    try:
        connection.request(method, url)
        return connection.getresponse().read()
    except:
        tidy_up()
        sys.stderr.write('{0}\n'.format(message))
        sys.exit(1)


def get_mbeans(json):
    # This sorts out the annoying { solr-mbeans: [ "THING1", { actualContentOfThing1: {} }, "THING2", { actualContentOfThing2: {} } ] }
    # that Solr does by turning it into { mbeans: { THING1: { actualContentOfThing1: {} }, THING2: { actualContentOfThing2: {} } } }
    unconverted_mbeans = json['solr-mbeans']
    mbeans = {}
    name = None
    for thing in unconverted_mbeans:
        if name is None:
            name = thing
        else:
            mbeans[name] = thing
            name = None
    return mbeans

def system_stats(core_name, omit_jvm_stats):
    system_content = request_and_response_or_bail('GET', '/{0}/admin/system?wt=json&_={1}'.format(core_name, timestamp_millis), 'Error while retrieving system stats')
    system_json = json.loads(system_content)
    if not omit_jvm_stats:
        print '{0}.{1} {2} {3}'.format(prefix, 'jvm.uptimeMillis', system_json['jvm']['jmx']['upTimeMS'], timestamp)
        print '{0}.{1} {2} {3}'.format(prefix, 'jvm.memory.free', system_json['jvm']['memory']['raw']['free'], timestamp)
        print '{0}.{1} {2} {3}'.format(prefix, 'jvm.memory.max', system_json['jvm']['memory']['raw']['max'], timestamp)
        print '{0}.{1} {2} {3}'.format(prefix, 'jvm.memory.total', system_json['jvm']['memory']['raw']['total'], timestamp)
        print '{0}.{1} {2} {3}'.format(prefix, 'jvm.memory.used', system_json['jvm']['memory']['raw']['used'], timestamp)
        print '{0}.{1} {2} {3}'.format(prefix, 'jvm.processors', system_json['jvm']['processors'], timestamp)
    print '{0}.{1} {2} {3}'.format(prefix, 'system.committedVirtualMemorySize', system_json['system']['committedVirtualMemorySize'], timestamp)
    print '{0}.{1} {2} {3}'.format(prefix, 'system.freePhysicalMemorySize', system_json['system']['freePhysicalMemorySize'], timestamp)
    print '{0}.{1} {2} {3}'.format(prefix, 'system.freeSwapSpaceSize', system_json['system']['freeSwapSpaceSize'], timestamp)
    print '{0}.{1} {2} {3}'.format(prefix, 'system.maxFileDescriptorCount', system_json['system']['maxFileDescriptorCount'], timestamp)
    print '{0}.{1} {2} {3}'.format(prefix, 'system.openFileDescriptorCount', system_json['system']['openFileDescriptorCount'], timestamp)
    print '{0}.{1} {2} {3}'.format(prefix, 'system.processCpuTime', system_json['system']['processCpuTime'], timestamp)
    print '{0}.{1} {2} {3}'.format(prefix, 'system.systemLoadAverage', system_json['system']['systemLoadAverage'], timestamp)
    print '{0}.{1} {2} {3}'.format(prefix, 'system.totalPhysicalMemorySize', system_json['system']['totalPhysicalMemorySize'], timestamp)
    print '{0}.{1} {2} {3}'.format(prefix, 'system.totalSwapSpaceSize', system_json['system']['totalSwapSpaceSize'], timestamp)

def query_handler_stats(stats, name, core_name):
    print '{0}.{1}.queryHandlers.{2}.{3} {4} {5}'.format(prefix, core_name, name, '15minRateReqsPerSecond', stats['15minRateReqsPerSecond'], timestamp)
    print '{0}.{1}.queryHandlers.{2}.{3} {4} {5}'.format(prefix, core_name, name, '5minRateReqsPerSecond', stats['5minRateReqsPerSecond'], timestamp)
    print '{0}.{1}.queryHandlers.{2}.{3} {4} {5}'.format(prefix, core_name, name, '75thPcRequestTime', stats['75thPcRequestTime'], timestamp)
    print '{0}.{1}.queryHandlers.{2}.{3} {4} {5}'.format(prefix, core_name, name, '95thPcRequestTime', stats['95thPcRequestTime'], timestamp)
    print '{0}.{1}.queryHandlers.{2}.{3} {4} {5}'.format(prefix, core_name, name, '999thPcRequestTime', stats['999thPcRequestTime'], timestamp)
    print '{0}.{1}.queryHandlers.{2}.{3} {4} {5}'.format(prefix, core_name, name, '99thPcRequestTime', stats['99thPcRequestTime'], timestamp)
    print '{0}.{1}.queryHandlers.{2}.{3} {4} {5}'.format(prefix, core_name, name, 'avgRequestsPerSecond', stats['avgRequestsPerSecond'], timestamp)
    print '{0}.{1}.queryHandlers.{2}.{3} {4} {5}'.format(prefix, core_name, name, 'avgTimePerRequest', stats['avgTimePerRequest'], timestamp)
    print '{0}.{1}.queryHandlers.{2}.{3} {4} {5}'.format(prefix, core_name, name, 'errors', stats['errors'], timestamp)
    print '{0}.{1}.queryHandlers.{2}.{3} {4} {5}'.format(prefix, core_name, name, 'handlerStart', stats['handlerStart'], timestamp)
    print '{0}.{1}.queryHandlers.{2}.{3} {4} {5}'.format(prefix, core_name, name, 'medianRequestTime', stats['medianRequestTime'], timestamp)
    print '{0}.{1}.queryHandlers.{2}.{3} {4} {5}'.format(prefix, core_name, name, 'requests', stats['requests'], timestamp)
    print '{0}.{1}.queryHandlers.{2}.{3} {4} {5}'.format(prefix, core_name, name, 'timeouts', stats['timeouts'], timestamp)
    print '{0}.{1}.queryHandlers.{2}.{3} {4} {5}'.format(prefix, core_name, name, 'totalTime', stats['totalTime'], timestamp)

def update_handler_stats(stats, core_name):
    print '{0}.{1}.updateHandler.{2} {3} {4}'.format(prefix, core_name, 'adds', stats['adds'], timestamp)
    print '{0}.{1}.updateHandler.{2} {3} {4}'.format(prefix, core_name, 'autoCommits', stats['autocommits'], timestamp)
    print '{0}.{1}.updateHandler.{2} {3} {4}'.format(prefix, core_name, 'commits', stats['commits'], timestamp)
    print '{0}.{1}.updateHandler.{2} {3} {4}'.format(prefix, core_name, 'cumulativeAdds', stats['cumulative_adds'], timestamp)
    print '{0}.{1}.updateHandler.{2} {3} {4}'.format(prefix, core_name, 'cumulativeDeletesById', stats['cumulative_deletesById'], timestamp)
    print '{0}.{1}.updateHandler.{2} {3} {4}'.format(prefix, core_name, 'cumulativeDeletesByQuery', stats['cumulative_deletesByQuery'], timestamp)
    print '{0}.{1}.updateHandler.{2} {3} {4}'.format(prefix, core_name, 'cumulativeErrors', stats['cumulative_errors'], timestamp)
    print '{0}.{1}.updateHandler.{2} {3} {4}'.format(prefix, core_name, 'deletesById', stats['deletesById'], timestamp)
    print '{0}.{1}.updateHandler.{2} {3} {4}'.format(prefix, core_name, 'deletesByQuery', stats['deletesByQuery'], timestamp)
    print '{0}.{1}.updateHandler.{2} {3} {4}'.format(prefix, core_name, 'docsPending', stats['docsPending'], timestamp)
    print '{0}.{1}.updateHandler.{2} {3} {4}'.format(prefix, core_name, 'errors', stats['errors'], timestamp)
    print '{0}.{1}.updateHandler.{2} {3} {4}'.format(prefix, core_name, 'expungeDeletes', stats['expungeDeletes'], timestamp)
    print '{0}.{1}.updateHandler.{2} {3} {4}'.format(prefix, core_name, 'optimizes', stats['optimizes'], timestamp)
    print '{0}.{1}.updateHandler.{2} {3} {4}'.format(prefix, core_name, 'rollbacks', stats['rollbacks'], timestamp)
    print '{0}.{1}.updateHandler.{2} {3} {4}'.format(prefix, core_name, 'softAutoCommits', stats['soft autocommits'], timestamp)
    print '{0}.{1}.updateHandler.{2} {3} {4}'.format(prefix, core_name, 'transactionLogsTotalNumber', stats['transaction_logs_total_number'], timestamp)
    print '{0}.{1}.updateHandler.{2} {3} {4}'.format(prefix, core_name, 'transactionLogsTotalSize', stats['transaction_logs_total_size'], timestamp)

def cache_stats(stats, core_name, name):
    print '{0}.{1}.caches.{2}.{3} {4} {5}'.format(prefix, core_name, name, 'cumulativeEvictions', stats['cumulative_evictions'], timestamp)
    print '{0}.{1}.caches.{2}.{3} {4} {5}'.format(prefix, core_name, name, 'cumulativeHitRatio', stats['cumulative_hitratio'], timestamp)
    print '{0}.{1}.caches.{2}.{3} {4} {5}'.format(prefix, core_name, name, 'cumulativeHits', stats['cumulative_hits'], timestamp)
    print '{0}.{1}.caches.{2}.{3} {4} {5}'.format(prefix, core_name, name, 'cumulativeInserts', stats['cumulative_inserts'], timestamp)
    print '{0}.{1}.caches.{2}.{3} {4} {5}'.format(prefix, core_name, name, 'cumulativeLookups', stats['cumulative_lookups'], timestamp)
    print '{0}.{1}.caches.{2}.{3} {4} {5}'.format(prefix, core_name, name, 'evictions', stats['evictions'], timestamp)
    print '{0}.{1}.caches.{2}.{3} {4} {5}'.format(prefix, core_name, name, 'hitRatio', stats['hitratio'], timestamp)
    print '{0}.{1}.caches.{2}.{3} {4} {5}'.format(prefix, core_name, name, 'hits', stats['hits'], timestamp)
    print '{0}.{1}.caches.{2}.{3} {4} {5}'.format(prefix, core_name, name, 'inserts', stats['inserts'], timestamp)
    print '{0}.{1}.caches.{2}.{3} {4} {5}'.format(prefix, core_name, name, 'lookups', stats['lookups'], timestamp)
    print '{0}.{1}.caches.{2}.{3} {4} {5}'.format(prefix, core_name, name, 'size', stats['size'], timestamp)
    print '{0}.{1}.caches.{2}.{3} {4} {5}'.format(prefix, core_name, name, 'warmupTime', stats['warmupTime'], timestamp)

def core_stats(core_name):
    mbeans_content = request_and_response_or_bail('GET', '/{0}/admin/mbeans?stats=true&wt=json&_={1}'.format(core_name, timestamp_millis), 'Error while retrieving core stats')
    mbeans_json = get_mbeans(json.loads(mbeans_content))
    searcher_stats = mbeans_json['CORE']['searcher']['stats']
    print '{0}.{1}.{2} {3} {4}'.format(prefix, core_name, 'numDocs', searcher_stats['numDocs'], timestamp)
    print '{0}.{1}.{2} {3} {4}'.format(prefix, core_name, 'maxDoc', searcher_stats['maxDoc'], timestamp)
    print '{0}.{1}.{2} {3} {4}'.format(prefix, core_name, 'numSegments', searcher_stats['numSegments'], timestamp)
    print '{0}.{1}.{2} {3} {4}'.format(prefix, core_name, 'deletedDocs', searcher_stats['deletedDocs'], timestamp)
    print '{0}.{1}.{2} {3} {4}'.format(prefix, core_name, 'indexVersion', searcher_stats['indexVersion'], timestamp)
    print '{0}.{1}.{2} {3} {4}'.format(prefix, core_name, 'warmupTime', searcher_stats['warmupTime'], timestamp)
    core_stats = mbeans_json['CORE']['core']['stats']
    print '{0}.{1}.{2} {3} {4}'.format(prefix, core_name, 'refCount', core_stats['refCount'], timestamp)
    query_handler_stats(mbeans_json['QUERYHANDLER']['dismax']['stats'], 'dismax', core_name)
    query_handler_stats(mbeans_json['QUERYHANDLER']['org.apache.solr.handler.UpdateRequestHandler']['stats'], 'update', core_name)
    query_handler_stats(mbeans_json['QUERYHANDLER']['standard']['stats'], 'standard', core_name)
    query_handler_stats(mbeans_json['QUERYHANDLER']['warming']['stats'], 'warming', core_name)
    update_handler_stats(mbeans_json['UPDATEHANDLER']['updateHandler']['stats'], core_name)
    cache_stats(mbeans_json['CACHE']['documentCache']['stats'], core_name, 'documentCache')
    cache_stats(mbeans_json['CACHE']['fieldValueCache']['stats'], core_name, 'fieldValueCache')
    cache_stats(mbeans_json['CACHE']['filterCache']['stats'], core_name, 'filterCache')
    cache_stats(mbeans_json['CACHE']['nCache']['stats'], core_name, 'nCache')
    cache_stats(mbeans_json['CACHE']['queryResultCache']['stats'], core_name, 'queryResultCache')
    print '{0}.{1}.caches.fieldCache.{2} {3} {4}'.format(prefix, core_name, 'entriesCount', mbeans_json['CACHE']['fieldCache']['stats']['entries_count'], timestamp)
    print '{0}.{1}.caches.fieldCache.{2} {3} {4}'.format(prefix, core_name, 'insanityCount', mbeans_json['CACHE']['fieldCache']['stats']['insanity_count'], timestamp)

cores_content = request_and_response_or_bail('GET', '/admin/cores?wt=json&indexInfo=true&_={0}'.format(timestamp_millis), 'Error while retrieving cores.')
cores_json = json.loads(cores_content)

core_names = cores_json['status'].keys()

if len(core_names) == 0:
    tidy_up()
    sys.stderr.write('No cores\n')
    sys.exit(1)

first_core_name = core_names[0]

system_stats(first_core_name, omit_jvm_stats)

for core_name in core_names:
    core_stats(core_name)

tidy_up()
