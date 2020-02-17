from django.db import models
from datetime import date
from PIL import Image, ImageDraw
import urllib.request
import json
import boto3
import os

class Posting(models.Model):
    id = models.CharField(max_length=64, primary_key=True, editable=False)
    title = models.CharField(max_length=64, default='')
    company = models.CharField(max_length=64, default='')

    city = models.CharField(max_length=20, default='')
    state = models.CharField(max_length=8, default='')
    country = models.CharField(max_length=16, default='')

    source = models.CharField(max_length=16, default='')
    date_posted = models.DateField(default=date.today)
    url = models.URLField(default='')
    vector = models.CharField(max_length=2048, default='')
    description = models.CharField(max_length=256, default='')
    image_url = models.URLField(blank=True)
    # logo = models.URLField(default='')
    
    # default_logo = default.jpg
    # will need to add this to produce images
    # need to have default "no image" jpeg

    def get_image_url(self):
        if self.image_url is None:
            image = self.generate_image()
            self.image_url = self.save_image(image)
        return self.image_url

    def generate_image(self):
        # title = self.tile to access parameters
        # each posting has company logo, job title, experience level, location, and posting link
        #img = Image.new('RGB', (570, 430), color = (255, 255, 255))
        if self.logo is None: 
            logo = default_logo
            self.logo = self.save_logo(logo)
        img = Image.open(self.logo_url) 
        #i'm not entirely sure this will work lmao 

        #draw the image 
        draw = ImageDraw.Draw(img)
        draw.line((0, 0) + img.size, fill=(0,0,0))
        draw.text((0, 0) + img.size, self.title, fill=(0,0,0))
        draw.text((0, 0) + img.size + 20, self.company + "• Full Time", fill = (0,0,0))
        draw.line((0, 0) + img.size + 60, fill = (0,0,0))
        url = id + company + title + ".jpg"
        img.save(url)
        #pass

    def save_image(self, image):
        """ 
        Save to Amazon S3
  
        Parameters: 
            image (TBD):
          
        Returns:
            image_url (string): a publically access url string
        """
        pass

    #Takes in a company name and bucket location for upload
    #and uploads the file to S3, and returns the s3 file name
    def load_logo(self, company, bucket):
        #Get company autocomplete and values
        url = "https://autocomplete.clearbit.com/v1/companies/suggest?query=" + company
        searchResult = urllib.request.urlopen(url)
        data = searchResult.read()
        encodedData = searchResult.info().get_content_charset('utf-8')
        resultingData = json.loads(data.decode(encodedData))
        
        #Download Logo locally
        for item in resultingData: 
            clearbitURL = item["logo"]
            imageFilename = company + ".png"
            urllib.request.urlretrieve(clearbitURL, imageFilename)
            break
        
        ACCESS_KEY = os.environ['ACCESS_KEY']
        SECRET_KEY = os.environ['SECRET_KEY']
        
        #Upload to S3
        s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
        s3.upload_file(imageFilename, bucket, imageFilename)
        
        #Delete local image
        os.remove(imageFilename)
        
        return imageFilename
    
    def __str__(self):
        return '{:39}{:24}{:24}{}\t{:70}'.format(self.title[:35], self.company[:20],
                self.city[:20], self.date_posted, self.url[:70])
