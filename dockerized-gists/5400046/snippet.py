import pyrax
import os
import sys
import datetime
from novaclient import exceptions


#Loading credentials from ini file
def auth(credential_location="~/.rackspace_cloud_credentials"):
    """
    Loads the pyrax credentials from ~/.rackspace_cloud_credentials
    :param credential_location: The location containing the credential ini
    """
    credentials = os.path.expanduser(credential_location)
    pyrax.set_credential_file(credentials)



def create_image(server, image_name=""):
    """
    Creates an image of the given server.
    :param server: A valid Server object
    :param image_name: The desired name for the image.
    :return: The uuid of the generated image. :raise: Any exceptions generated from the client
    """
    if image_name == "":
        image_name = str(server.name)

    try:
        image_uuid = server.create_image(image_name)
    except exceptions.ClientException as e:
        print "Unable to create image at this time: " + e.message
        sys.exit(1)

    print "Creating image: ", image_name
    return image_uuid


def main():
    auth()

    #Creating cloudserver client
    cs = pyrax.connect_to_cloudservers(region="ORD")
    server_uuid = 'FILL_IN_YOUR_SERVER_UUID_HERE'
    image_name = "ROLLING_IMAGE_NAME"

    print "Looking for old images named %s" % image_name
    old_images = cs.images.findall(name=image_name)

    print "Finding server from uuid %s" % server_uuid
    server = cs.servers.get(server=server_uuid)

    print "Creating new image of %s named %s" % (server.name, image_name)
    image_uuid = create_image(server, image_name=image_name)

    print "New image created: %s" % image_uuid

    for image in old_images:
        print "Deleting Old Image: %s --  %s" % (image.name, image.id)
        cs.images.delete(image.id)

if __name__ == '__main__':
    main()
