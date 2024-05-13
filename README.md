<!-- 11/05/2024. -->

# fastapi_learning

Documentation of my [FastAPI](https://fastapi.tiangolo.com/learn/) learning process. I document what I find necessary.

Posts are listed in the [Related post(s)](#related-posts) section below. Each entry includes the link to the actual post, the ``git clone`` command for the target code revision, and an excerpt from the post.

## Related post(s)

1. [Python FastAPI: Some Further Studies on OAuth2 Security](https://behainguyen.wordpress.com/2024/05/11/python-fastapi-some-further-studies-on-oauth2-security/)

```
git clone -b v0.1.0 https://github.com/behai-nguyen/fastapi_learning.git
```

``FastAPI`` provides [excellent tutorials](https://fastapi.tiangolo.com/learn/) that thoroughly introduce the framework. Two sections on security, namely [Tutorial - User Guide Security](https://fastapi.tiangolo.com/tutorial/security/) and [Advanced User Guide Security](https://fastapi.tiangolo.com/advanced/security/), have sparked further questions, which we are discussing in this post. Hopefully, this discussion will lead to a better understanding of how ``FastAPI`` security works.

2. [Python FastAPI: Integrating OAuth2 Security with the Application's Own Authentication Process](https://behainguyen.wordpress.com/2024/05/13/python-fastapi-integrating-oauth2-security-with-the-applications-own-authentication-process/)

```
git clone -b v0.2.0 https://github.com/behai-nguyen/fastapi_learning.git
```

In the [first post](https://behainguyen.wordpress.com/2024/05/11/python-fastapi-some-further-studies-on-oauth2-security/), we explore some aspects of ``OAuth2`` authentication, focusing on the ``/token`` path as illustrated in an example from the [Simple OAuth2 with Password and Bearer](https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/) 
section of the [Tutorial - User Guide Security](https://fastapi.tiangolo.com/tutorial/security/). In this subsequent post, we implement our own custom preliminary login process, leveraging the ``/token`` path. This means that both the Swagger UI ``Authorize`` button and our application's login button utilise the same server code.

## License
[MIT license](http://www.opensource.org/licenses/mit-license.php)
and the [GPL license](http://www.gnu.org/licenses/gpl.html).
