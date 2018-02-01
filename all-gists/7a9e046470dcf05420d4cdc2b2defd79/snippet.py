# coding: utf-8

from amazon.api import AmazonAPI
from amazon.api import AmazonException, LookupException, AsinNotFound


class AmazonAPIWrapper(object):
    """
    pip install python-amazon-simple-product-api
    """
    def __init__(self, account):
        self.account = account

    def __enter__(self):
        self.API = AmazonAPI(
            self.account["ACCESS_KEY"],
            self.account["SECRET_KEY"],
            self.account["ASSOC_TAG"],
            region = self.account["REGION"] if "REGION" in self.account else "US")
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        pass

    def Lookup(self, **kwargs):
        if "ItemId" not in kwargs:
            raise AmazonException("Not Set ItemId")

        if isinstance(kwargs["ItemId"], list):
            kwargs["ItemId"] = ",".join(kwargs["ItemId"])

        response = self.API.lookup(**kwargs)
        if hasattr(response, "__iter__"):
            for item in response:
                self.item = item
                yield self
        else:
            self.item = response
            yield self

    def inches2cm(self, data):
        return round(float(data) / 100 * 2.54, 2)

    def pounds2g(self, data):
        return round(float(data) / 100 * 0.4536 * 1000, 2)

    @property
    def region(self):
        return self.API.region

    @property
    def asin(self):
        return self.item.asin

    @property
    def title(self):
        return self.item.title

    @property
    def category(self):
        if len(self.item.browse_nodes) > 0:
            for i in range(len(self.item.browse_nodes)):
                name = self.item.browse_nodes[i].ancestors[-1].name
                if name == "jp-stores":
                    continue
                elif name is not None:
                    break
            
            if hasattr(name, "text"):
                return name.text
            else:
                return name
        else:
            return None

    @property
    def browsenode_id(self):
        if len(self.item.browse_nodes) > 0:
            for i in range(len(self.item.browse_nodes)):
                name = self.item.browse_nodes[i].ancestors[-1].name
                if name == "jp-stores":
                    continue
                else:
                    return self.item.browse_nodes[i].id
        else:
            return None

    @property
    def image_url(self):
        if self.item.medium_image_url:
            return str(self.item.medium_image_url)

    @property
    def attributes(self):
        return self.item.get_attributes([
            "PackageDimensions.Weight",
            "PackageDimensions.Width",
            "PackageDimensions.Height",
            "PackageDimensions.Length"
        ])

    @property
    def weight(self):
        if "PackageDimensions.Weight" in self.attributes:
            return self.pounds2g(self.attributes["PackageDimensions.Weight"])

    @property
    def raw_weight(self):
        if "PackageDimensions.Weight" in self.attributes:
            return self.attributes["PackageDimensions.Weight"]

    @property
    def width(self):
        if "PackageDimensions.Width" in self.attributes:
            return self.inches2cm(self.attributes["PackageDimensions.Width"])

    @property
    def raw_width(self):
        if "PackageDimensions.Width" in self.attributes:
            return self.attributes["PackageDimensions.Width"]

    @property
    def height(self):
        if "PackageDimensions.Height" in self.attributes:
            return self.inches2cm(self.attributes["PackageDimensions.Height"])

    @property
    def raw_height(self):
        if "PackageDimensions.Height" in self.attributes:
            return self.attributes["PackageDimensions.Height"]

    @property
    def length(self):
        if "PackageDimensions.Length" in self.attributes:
            return self.inches2cm(self.attributes["PackageDimensions.Length"])

    @property
    def raw_length(self):
        if "PackageDimensions.Length" in self.attributes:
            return self.attributes["PackageDimensions.Length"]

    @property
    def price(self):
        price, currency = self.item.price_and_currency
        return price

    @property
    def publication_date(self):
        return self.item.publication_date

    @property
    def release_date(self):
        return self.item.release_date

    @property
    def sales_rank(self):
        return self.item.sales_rank

    @property
    def total_new(self):
        return self.item._safe_get_element_text('OfferSummary.TotalNew')

    @property
    def brand(self):
        return self.item.brand

    @property
    def manufacturer(self):
        return self.item.manufacturer

    @property
    def ean(self):
        return self.item.ean

if __name__ == "__main__":

    account = {
        "ACCESS_KEY": "ACCESS_KEY",
        "SECRET_KEY": "SECRET_KEY",
        "ASSOC_TAG": "associate-tag"
    }

    with AmazonAPIWrapper(account) as API:
        try:
            #API.setAsinFromFile(file)
            #api.Asin = ["B00F5JOIT0", "B00TS0UK0I", "B00O9GPEAC"]
            API.Asin = "B017VFHDKQ"
            for item in API.Lookup():
                print(item.total_new)
        except Exception as e:
            print(e)