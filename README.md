# s3-now

> Stop thinking about key-value stores, or image storage for every hobby project.
> Instead add a single s3-now deployment to simplify all your other projects.

s3-now is a generic AWS Lambda function that adds an HTTP API capability to S3.
It should be used as service for your other backend services to handle file-, image-
and JSON application data.

## Getting started

```
# Add serverless cli
yarn global add serverless

# Configure serverless with your AWS keys
sls config credentials --provider aws

# Clone this repository
git clone git@github.com:tomfa/s3-now

# Copy and setup environment variables
cp dev-template.env .env

# Add your private key, can be any string
echo 'PRIVATE_JWT_KEY=ANY-STRING-DIFFICULT-TO-GUESS' >> .env

# Set allowed projects
echo 'ALLOWED_PROJECTS=myproject-<MYPROJECT-API-KEY>' >> .env

# Spin the service up in AWS
sls deploy
```

## Developing

### Built With
Serverless, Python 3.7, AWS S3, AWS Lambda

### Prerequisites
- An [AWS Account](https://aws.amazon.com/getting-started/), with access- and secret keys set up.
- [Serverless](https://serverless.com) cli installed.

### Configuration

#### Set or update your private key
If you wish to change your private key, edit the `.env` file:
```
PRIVATE_JWT_KEY=ANY-STRING-DIFFICULT-TO-GUESS
```
Note that this invalidates all token previously generated, and should only be done
in the initial configuration of the service, or after a potential breach.

The public key, needed for inspecting public data in tokens, will become 
accessable at the URL: `/public-key`

#### Setting allowed consumers
Set names of your consumers and add their unique API-keys by editing the `.env` file:
```
ALLOWED_PROJECTS=myproject-1e8c26c8-a0cc-45f6-9ec4-9d4b070d99c7
```

Here, s3-now will recognize the application `myproject`, and require API-key
`1e8c26c8-a0cc-45f6-9ec4-9d4b070d99c7`. You can add multiple projects and keys
by separating them with comma:
```
ALLOWED_PROJECTS=myproject-1e8c26c8-a0cc-45f6-9ec4-9d4b070d99c7,otherproject-1e8c26c8-a0cc-45f6-9ec4-9d4b070d99c8
```

## API Reference 

### Adding JSON data
This will add the key `my-data` and set its value to `fish`. It will not 
affect other keys. The data must be valid JSON.
```
curl -X POST -H "Authorization: Basic <MY-API-KEY>" \
    -d '{"my-data": { "cheese": "pecorino"}}' \
    https://my-s3-now-url/json/
```

Alternatively, you can also specify keys with the URL
```
curl -X POST -H "Authorization: Basic <MY-API-KEY>" \
    -d '{ "cheese": "pecorino"}' \
    https://my-s3-now-url/json/my-data
```

### Retrieving JSON data
JSON Data can be retrieved via `key` parameter. The examples below will 
now return `pecorino`.
```
curl -H "Authorization: Basic <MY-API-KEY>" \
    https://my-s3-now-url/json/?key=my-data.cheese
```

Alternatively, you can also specify it via the URL
```
curl -H "Authorization: Basic <MY-API-KEY>" \
    https://my-s3-now-url/json/my-data/cheese
```

### Upload file via HTML form
To upload via a form, your backend-service will have to generate a token to 
be used when files are posted.

If you wish to let the user upload a file to our storage, you should first 
assign a key that will be point to the file. Let's use `user/1/favorite-pic` 
as an example key.

#### Generating an upload token
```
curl -X POST -H "Authorization: Basic <MY-API-KEY>" \
    -d '{"key":"user/1/favorite-pic", methods=["POST"]' \
    https://my-s3-now-url/token/
```

This may return a token like 
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJtZXRob2RzIjpbIlBPU1QiXSwia2V5IjoidXNlcnMvMS9pbWFnZXMvMTIzIiwiYXBwIjoiTXlFeGFtcGxlQXBwIiwiaWF0IjoxNTE2MjM5MDIyfQ.KLPsXrlZC3e-BAgq5hDYO78NTevlr-_r58ecAWo1jo8
```

#### Adding an upload form in frontend application

Add the token generated previously to a hidden input named `token` in your 
HTML form:
```
<form action="https://my-s3-now-url/file/" method="POST">
  <input name="token" type="hidden" value="eyJhbGciOiJIUzI1NiIsIn..." />
  <input name="file" type="file" />
</form>
```

### Linking to the file
s3-now is not meant to be a static file location for your project. It's 
rather a service for holding dynamic application data like user-settings 
(The JSON service) plus photos and files (the file service).

Therefore, all files that are uploaded are by default private, and can 
not be retrieved by knowing the key or guessing the URL. To use the services,
your backend will have to retrieve these through authenticated calls and 
forwarded to the front end application. Alternatively, JWT access tokens 
can be generated to be given to the frontend application, that holds the 
keys or key-prefixes that they'll have access to. 

#### Generating links to files

You can generate tokens to be used for retrieving a one or more 
*specific files* by specifying the keys in a payload against `/token`. 
Remove the `method` payload that was previously specified, as `GET` is default.
```
curl -X POST -H "Authorization: Basic <MY-API-KEY>" \
    -d '{"keys":["user/1/favorite-pic"]}' \
    https://my-s3-now-url/token/
```

This will return a token ala ```eyJhbGciOiJIUzI1N...```, which in 
turn can be added to links like this:
```
<a href="https://my-s3-now-url/files/user/1/favorite-pic?token=eyJhbGciOiJIUzI1N...">
  See my grandmother
</a>
```

It can get tiresome to generate tokens via a request for each file
you want to expose in your frontend application. In addition to being able
to specify multiple keys in the payload, you can also generate a token that
is authorized to retrieve any key that is prefixed with a specific label.

For instance, to generate a token that have access any key that starts
with `users/1/`, simply add a * at the end of the key, e.g.
```
curl -X POST -H "Authorization: Basic <MY-API-KEY>" \
    -d '{"key":"users/1/*"}' \
    https://my-s3-now-url/url/
```

## Customizing s3-now for your use
s3-now may not quite fit your needs. If it doesn't, simply change it, and 
deploy it. Our code is your code ❤️


### Deploy any updates
If you do changes to the code and wish to deploy, simply run:

```
sls deploy
```

### Using custom buckets

s3-now will include setup of a generic S3-bucket and CloudFront cache. You do 
not have to set up individual buckets per project that uses it. s3-now handles
separation of storage within the generic bucket, so that data won't leak from
one app into the other or visa versa.

If you wish to use existing buckets, you will have to set them up in your own 
way, and pass the bucket name, plus your access- and secret key as parameters
when using the API.

## Licensing
MIT
