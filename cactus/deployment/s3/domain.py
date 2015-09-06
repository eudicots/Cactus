import types
import logging

from boto.route53.connection import Route53Connection
from boto.route53.record import ResourceRecordSets

from boto.s3.connection import S3Connection
from boto.s3.website import RedirectLocation

# Generic steps for custom domains can be found here
# http://docs.aws.amazon.com/AmazonS3/latest/dev/website-hosting-custom-domain-walkthrough.html

# Hosted zone tables

# https://forums.aws.amazon.com/thread.jspa?threadID=116724
# http://docs.aws.amazon.com/general/latest/gr/rande.html#s3_region

# Amazon, you owe me four hours of my life...

HOSTED_ZONES = {
    # US Standard
    "s3-website-us-east-1.amazonaws.com": "Z3AQBSTGFYJSTF",
    # US West (Oregon) Region
    "s3-website-us-west-2.amazonaws.com": "Z3BJ6K6RIION7M",
    # US West (Northern California) Region
    "s3-website-us-west-1.amazonaws.com": "Z2F56UZL2M1ACD",
    # EU (Ireland) Region
    "s3-website-eu-west-1.amazonaws.com": "Z1BKCTXD74EZPE",
    # Asia Pacific (Singapore) Region
    "s3-website-ap-southeast-1.amazonaws.com": "Z3O0J2DXBE1FTB",
    # Asia Pacific (Sydney) Region
    "s3-website-ap-southeast-2.amazonaws.com": "Z1WCIGYICN2BYD",
    # Asia Pacific (Tokyo) Region
    "s3-website-ap-northeast-1.amazonaws.com": "Z2M4EHUR26P7ZW",
    # South America (Sao Paulo) Region
    "s3-website-sa-east-1.amazonaws.com": "Z7KQH4QJS55SO",
    # AWS GovCloud (US)
    "s3-website-us-gov-west-1.amazonaws.com": "Z31GFT0UA1I2HV",
}


class AWSBucket(object):

    def __init__(self, accessKey, secretKey, name):

        self.name = name

        self.accessKey = accessKey
        self.secretKey = secretKey

        self.connection = S3Connection(
            aws_access_key_id=accessKey,
            aws_secret_access_key=secretKey,
        )

        self._cache = {}

    def bucket(self):
        try:
            return self.connection.get_bucket(self.name)
        except:
            return None

    def create(self):
        logging.info('Create bucket %s', self.name)
        self.connection.create_bucket(self.name, policy='public-read')

    def isCreated(self):
        return self.bucket() is not None

    def configureWebsite(self):
        logging.info('Configuring website endpoint %s', self.name)
        self.bucket().configure_website('index.html', 'error.html')

    def configureRedirect(self, url):
        logging.info('Setup redirect %s -> %s', self.name, url)
        self.bucket().configure_website(
            redirect_all_requests_to=RedirectLocation(hostname=url))

    def websiteEndpoint(self):
        return self.bucket().get_website_endpoint()




class AWSDomain(object):

    def __init__(self, accessKey, secretKey, domain):

        self.domain = domain

        self.accessKey = accessKey
        self.secretKey = secretKey

        self.connection = Route53Connection(
            aws_access_key_id=accessKey,
            aws_secret_access_key=secretKey,
        )

        self._cache = {}

    @property
    def id(self):
        return self.hostedZone()['HostedZone']['Id'].replace('/hostedzone/', '')

    @property
    def fullDomain(self):
        parts = self.domain.split(".")
        return parts[len(parts) - 2] + "." + parts[len(parts) - 1]

    @property
    def dnsDomain(self):
        return self.domain + "."

    def isValidDomain(self):
        pass

    def isNakedDomain(self):
        pass

    def records(self):
        pass

    def createHostedZone(self):

        logging.info('Creating hosted zone for %s', self.fullDomain)

        self.connection.create_hosted_zone(self.fullDomain)

    def hostedZone(self):
        if not "hostedZone" in self._cache:
            hostedZone = self.connection.get_hosted_zone_by_name(self.fullDomain)
            if not hostedZone:
                return
            self._cache["hostedZone"] = hostedZone.get("GetHostedZoneResponse", None)
        return self._cache["hostedZone"]

    def nameServers(self):
        hostedZone = self.hostedZone()

        if hostedZone:
            return self.hostedZone()["DelegationSet"]["NameServers"]
        else:
            return None

    def records(self):
        return self.connection.get_all_rrsets(self.id)

    def createRecord(self, name, recordType, values, ttl=60*60*3):
        self._changeRecord("CREATE", name, recordType, values, ttl)

    def deleteRecord(self, name, recordType, values, ttl=60*60*3):
        self._changeRecord("DELETE", name, recordType, values, ttl)

    def _changeRecord(self, change, name, recordType, values, ttl):

        logging.info('%s record %s:%s in zone %s', change, name, recordType, self.domain)

        if type(values) is not types.ListType:
            values = [values]

        changes = ResourceRecordSets(self.connection, self.id)
        change = changes.add_change(change, name, recordType, ttl)

        for value in values:
            change.add_value(value)

        changes.commit()


    def createAlias(self, name, recordType, aliasHostedZoneId, aliasDNSName, identifier=None, weight=None, comment=""):
        self._changeAlias("CREATE", name, recordType, aliasHostedZoneId, aliasDNSName, identifier, weight, comment)

    def deleteAlias(self, name, recordType, aliasHostedZoneId, aliasDNSName, identifier=None, weight=None, comment=""):
        self._changeAlias("DELETE", name, recordType, aliasHostedZoneId, aliasDNSName, identifier, weight, comment)

    def _changeAlias(self, change, name, recordType, aliasHostedZoneId, aliasDNSName, identifier, weight, comment):

        logging.info('%s alias %s:%s in zone %s', change, name, recordType, self.domain)

        changes = ResourceRecordSets(self.connection, self.id, comment)
        change = changes.add_change(change, name, recordType, identifier=identifier, weight=weight)
        change.set_alias(aliasHostedZoneId, aliasDNSName)
        changes.commit()


    def delete(self, record):

        if record.alias_dns_name:
            self.deleteAlias(record.name, record.type,
                record.alias_hosted_zone_id, record.alias_dns_name,
                identifier=record.identifier, weight=record.weight)
        else:
            self.deleteRecord(record.name, record.type, record.resource_records,
                ttl=record.ttl)

    def pointRootToBucket(self):

        # Make sure the correct bucket exists and is ours
        bucket = AWSBucket(self.accessKey, self.secretKey, self.domain)
        endpoint = bucket.websiteEndpoint()
        endpointDomain = endpoint[len(self.dnsDomain):]

        # Remove old A record for the root domain
        for record in self.records():
            if record.type in ["A", "CNAME"] and record.name == self.dnsDomain:
                self.delete(record)

        # Create new root domain record that points to the bucket
        self.createAlias(self.dnsDomain, "A", HOSTED_ZONES[endpointDomain], endpointDomain)


    def setupRedirect(self):

        redirectDomain = "www.%s" % self.domain
        redirectDNSDomain = redirectDomain + '.'

        bucket = AWSBucket(self.accessKey, self.secretKey, redirectDomain)

        if bucket.isCreated():
            logging.info("Bucket with name %s already exists, so skipping redirect bucket setup. \
                If you've set this up before, this will still work. Delete the bucket if you want Cactus to\
                set it up again.", redirectDomain)
            return

        bucket.create()
        bucket.configureRedirect(self.domain)

        for record in self.records():
            if record.type == "CNAME" and record.name == redirectDNSDomain:
                self.delete(record)

        self.createRecord(redirectDomain, "CNAME", [self.domain])

    def setup(self):

        if not self.hostedZone():
            self.createHostedZone()

        self.pointRootToBucket()

        if not self.domain.startswith("www."):
            self.setupRedirect()
