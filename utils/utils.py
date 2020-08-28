import subprocess
import boto3


def get_public_DNS():
    """

    :return: return public DNS of this local instance
    """
    cmd = ['wget', '-qO-', 'http://instance-data/latest/meta-data/public-ipv4/']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)

    o, _ = proc.communicate()
    return o.decode('ascii')


def get_instance_ID():
    """
    computes instance ID(sum of ip digits) for leader election purpose

    :return: the id of the instance (sum of ip digits)
    """
    # TODO ID is not atomic
    p_ip = get_public_DNS()
    return str(sum([int(x) for x in p_ip.split('.')]))


def get_instances():
    instances = []
    ec2 = boto3.client('ec2')
    response = ec2.describe_instances()

    for res in response['Reservations']:
        for inst in res['Instances']:
			if 'PublicIpAddress' in inst.keys():
				instances.append({'DNS': inst['PublicDnsName'],
								  'Adress': inst['PublicIpAddress'],
								  'ID': str(sum([int(x) for x in inst['PublicIpAddress'].split('.')]))
								  })
    return instances


def find_higher_ranks(nodes, my_rank):
    rv = []
    for node in nodes:
        if int(node['ID']) > int(my_rank):
            rv.append(node)

    return rv
