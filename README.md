<!-- 11/05/2024. -->

# fastapi_learning

Documentation of my [FastAPI](https://fastapi.tiangolo.com/learn/) learning process. I document what I find necessary.

Posts are listed in the [Related post(s)](#related-posts) section below. Each entry includes the link to the actual post, the ``git clone`` command for the target code revision, and an excerpt from the post.

## The Code After Tag v0.4.0 Requires Python 3.12.4

To install Python 3.12.4, please refer to the following post: [Installing Python 3.12.4 as an Additional Interpreter on Ubuntu 22.10 and Windows 10](https://behainguyen.wordpress.com/2024/06/28/installing-python-3-12-4-as-an-additional-interpreter-on-ubuntu-22-10-and-windows-10/).

### Preparing a New Virtual Environment ``venv`` Using Python 3.12.4

Simply remove the existing virtual environment ``venv`` and recreate it using the following command:

```
▶️Windows 10: F:\fastapi_learning>C:\PF\Python312\python.exe -m venv venv
▶️Ubuntu 22.10: behai@hp-pavilion-15:~/fastapi_learning$ /usr/local/bin/python3.12 -m venv venv
```

Verify the version of the Python interpreter in ``venv``:

```
▶️Windows 10: (venv) F:\fastapi_learning>venv\Scripts\python.exe --version
▶️Ubuntu 22.10: (venv) behai@hp-pavilion-15:~/fastapi_learning$ ./venv/bin/python --version
```

### Installing Third Party Packages

#### Run Time Packages

```
▶️Windows 10: (venv) F:\fastapi_learning>venv\Scripts\pip.exe install -e .
▶️Ubuntu 22.10: (venv) behai@hp-pavilion-15:~/fastapi_learning$ ./venv/bin/pip install -e .
```

#### Development Dependency Packages (for testing and development)

```
▶️Windows 10: (venv) F:\fastapi_learning>venv\Scripts\pip.exe install -e .[dev]
▶️Ubuntu 22.10: (venv) behai@hp-pavilion-15:~/fastapi_learning$ ./venv/bin/pip install -e .[dev]
```

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

3. [Python FastAPI: Implementing Persistent Stateful HTTP Sessions with Redis Session Middleware and Extending OAuth2PasswordBearer for OAuth2 Security](https://behainguyen.wordpress.com/2024/05/21/python-fastapi-implementing-persistent-stateful-http-sessions-with-redis-session-middleware-and-extending-oauth2passwordbearer-for-oauth2-security/)

```
git clone -b v0.3.0 https://github.com/behai-nguyen/fastapi_learning.git
```

In the <a href="https://behainguyen.wordpress.com/2024/05/13/python-fastapi-integrating-oauth2-security-with-the-applications-own-authentication-process/" title="Python FastAPI: Integrating OAuth2 Security with the Application’s Own Authentication Process" target="_blank">second post</a> of our <a href="https://fastapi.tiangolo.com/learn/" title="FastAPI" target="_blank">FastAPI</a> learning series, we implemented a placeholder for the application's own authentication process. In this post, we will complete this process by implementing persistent server-side HTTP sessions using the <a href="https://pypi.org/project/starsessions/" title="starsessions" target="_blank">starsessions</a> library and its <a href="https://redis.io/" title="Redis store" target="_blank">Redis store</a> store, as well as extending the <a href="https://fastapi.tiangolo.com/tutorial/security/first-steps/?h=oauth2passwordbearer#fastapis-oauth2passwordbearer" title="OAuth2PasswordBearer" target="_blank">OAuth2PasswordBearer</a> class.

4. [Python FastAPI: Complete Authentication Flow with OAuth2 Security](https://behainguyen.wordpress.com/2024/06/11/python-fastapi-complete-authentication-flow-with-oauth2-security/)

```
git clone -b v0.4.0 https://github.com/behai-nguyen/fastapi_learning.git
```

In the <a href="https://behainguyen.wordpress.com/2024/05/21/python-fastapi-implementing-persistent-stateful-http-sessions-with-redis-session-middleware-and-extending-oauth2passwordbearer-for-oauth2-security/" title="Python FastAPI: Implementing Persistent Stateful HTTP Sessions with Redis Session Middleware and Extending OAuth2PasswordBearer for OAuth2 Security" target="_blank">third post</a>, we implemented persistent stateful HTTP sessions. In this post, we will complete the application’s authentication UI flow. For the existing <code>/auth/token</code> and <code>/admin/me</code> routes, we will add functionality to conditionally return either HTML or JSON. Based on this new functionality, we will implement two new routes: <code>/api/login</code> and <code>/api/me</code>. These routes will only return JSON, and their endpoint handlers will be the same as those of the aforementioned routes respectively.

5. [Python FastAPI: Implementing Non-Blocking Logging with Built-In QueueHandler and QueueListener Classes](https://behainguyen.wordpress.com/2024/07/02/python-fastapi-implementing-non-blocking-logging-with-built-in-queuehandler-and-queuelistener-classes/)

```
git clone -b v0.5.0 https://github.com/behai-nguyen/fastapi_learning.git
```

Continuing with our <a href="https://github.com/behai-nguyen/fastapi_learning" title="Index of the Python FastAPI Complete Series" target="_blank">Python FastAPI learning series</a>, this post explores the implementation of non-blocking logging using Python’s built-in <a href="https://docs.python.org/3/library/logging.config.html#configuring-queuehandler-and-queuelistener" title="Configuring QueueHandler and QueueListener" target="_blank">QueueHandler and QueueListener classes</a>.

6. [Python FastAPI: Implementing SSL/HTTPS and CORS](https://behainguyen.wordpress.com/2024/07/25/python-fastapi-implementing-ssl-https-and-cors/)

```
git clone -b v0.6.0 https://github.com/behai-nguyen/fastapi_learning.git
```

In this installment of our <a href="https://github.com/behai-nguyen/fastapi_learning" title="Index of the Python FastAPI Complete Series" target="_blank">Python FastAPI learning series</a>, we explore the implementation of SSL/HTTPS for <code>localhost</code> and also the enabling of Cross-Origin Resource Sharing, or CORS.

7. [Python FastAPI: Enabling Database Support](https://behainguyen.wordpress.com/2024/08/04/python-fastapi-enabling-database-support/)

```
git clone -b v0.7.0 https://github.com/behai-nguyen/fastapi_learning.git
```

Continuing with our <a href="https://github.com/behai-nguyen/fastapi_learning" title="Index of the Python FastAPI Complete Series" target="_blank">Python FastAPI learning series</a>, in this installment, we enable database support for <a href="https://www.mysql.com/" title="MySQL database" target="_blank">MySQL</a>, <a href="https://www.postgresql.org/" title="PostgreSQL database" target="_blank">PostgreSQL</a>, and <a href="https://mariadb.com/" title="MariaDB database" target="_blank">MariaDB</a>. We will not add any new functionality; instead, the existing authentication process will check user information from a proper database instead of mock hard-coded data. We will also add a business logic layer responsible for data validation, enforcing business rules, etc.

8. [Python FastAPI: Fixing a Bug in the Authentication Process](https://behainguyen.wordpress.com/2024/08/26/python-fastapi-fixing-a-bug-in-the-authentication-process/)

```
git clone -b v0.8.0 https://github.com/behai-nguyen/fastapi_learning.git
```

In the <a href="https://behainguyen.wordpress.com/2024/06/11/python-fastapi-complete-authentication-flow-with-oauth2-security/" title="Python FastAPI: Complete Authentication Flow with OAuth2 Security" target="_blank">fourth post</a> of our <a href="https://github.com/behai-nguyen/fastapi_learning" title="Index of the Python FastAPI Complete Series" target="_blank">Python FastAPI learning series</a>, we introduced a bug in the authentication process. In this post, we describe the bug and discuss how to fix it.

9. [Python FastAPI: Implementing JSON Web Token](https://behainguyen.wordpress.com/2024/09/26/python-fastapi-implementing-json-web-token/)

```
git clone -b v0.9.0 https://github.com/behai-nguyen/fastapi_learning.git
```

Continuing with our <a href="https://github.com/behai-nguyen/fastapi_learning" title="Index of the Python FastAPI Complete Series" target="_blank">Python FastAPI learning series</a>, we will implement proper JSON Web Token (JWT) authentication as discussed in <a href="https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/" title="OAuth2 with Password (and hashing), Bearer with JWT tokens" target="_blank">the official tutorial</a>, with a few minor tweaks of our own.

10. [Python FastAPI: Implementing OAuth2 Scopes Part 01](https://behainguyen.wordpress.com/2024/10/08/python-fastapi-implementing-oauth2-scopes-part-01/)

```
git clone -b v0.10.0 https://github.com/behai-nguyen/fastapi_learning.git
```

In this part of our <a href="https://github.com/behai-nguyen/fastapi_learning" title="Index of the Python FastAPI Complete Series" target="_blank">Python FastAPI learning series</a>, we implement OAuth2 scopes. Our implementation is based on the advanced official tutorial on <a href="https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/" title="OAuth2 scopes" target="_blank">OAuth2 scopes</a>, with some variations of our own.

11. [Python FastAPI: OAuth2 Scopes Part 02 - UI Elements and User-Assigned Scopes](https://behainguyen.wordpress.com/2024/10/19/python-fastapi-oauth2-scopes-part-02-ui-elements-and-user-assigned-scopes/)

```
git clone -b v0.11.0 https://github.com/behai-nguyen/fastapi_learning.git
```

In the <a href="https://behainguyen.wordpress.com/2024/10/08/python-fastapi-implementing-oauth2-scopes-part-01/" title="Python FastAPI: Implementing OAuth2 Scopes Part 01" target="_blank">previous post</a>, we implemented <a href="https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/" title="OAuth2 scopes" target="_blank">OAuth2 scopes</a> for endpoint handler methods. This post extends that implementation to include <strong>UI elements</strong> — components that send HTTP requests to the server application.

12. [Python FastAPI: OAuth2 Scopes Part 03 - New CRUD Endpoints and User-Assigned Scopes](https://behainguyen.wordpress.com/2024/11/22/python-fastapi-oauth2-scopes-part-03-new-crud-endpoints-and-user-assigned-scopes/)

```
git clone -b v0.12.0 https://github.com/behai-nguyen/fastapi_learning.git
```

Continuing with the <a href="https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/" title="OAuth2 scopes" target="_blank">FastAPI OAuth2 scopes</a> topic, in this installment of our <a href="https://github.com/behai-nguyen/fastapi_learning" title="Index of the Complete Series" target="_blank"> Python FastAPI learning series</a>, we will implement seven (7) new routes that perform CRUD operations on the <code>employees</code> table. These new routes require scopes that we have implemented but have not used so far: <code>user:write</code>, <code>admin:read</code>, and <code>admin:write</code>. Please recall that we proposed this implementation in the <a href="https://behainguyen.wordpress.com/2024/10/19/python-fastapi-oauth2-scopes-part-02-ui-elements-and-user-assigned-scopes/#concluding-remarks" title="Python FastAPI: OAuth2 Scopes Part 02 - UI Elements and User-Assigned Scopes" target="_blank">last post</a>.

13. [Python FastAPI: Finishing Off the Pending Items, Code Cleanup, and Improvements](https://behainguyen.wordpress.com/2024/12/02/python-fastapi-finishing-off-the-pending-items-code-cleanup-and-improvements/)

```
git clone -b v0.13.0 https://github.com/behai-nguyen/fastapi_learning.git
```

In the last post of this <a href="https://github.com/behai-nguyen/fastapi_learning" title="Index of the Complete Series" target="_blank">Python FastAPI learning series</a>, we concluded with a list of <a href="https://behainguyen.wordpress.com/2024/11/22/python-fastapi-oauth2-scopes-part-03-new-crud-endpoints-and-user-assigned-scopes/#concluding-remarks" title="Python FastAPI: OAuth2 Scopes Part 03 - New CRUD Endpoints and User-Assigned Scopes" target="_blank">to-do items</a>. In this post, we will address these issues. Additionally, we are performing some code cleanup and improvements.

14. [Python FastAPI: Bug Fixing the Logout Process and Redis Session Cleanup](https://behainguyen.wordpress.com/2025/01/05/python-fastapi-bug-fixing-the-logout-process-and-redis-session-cleanup/)

```
git clone -b v0.14.0 https://github.com/behai-nguyen/fastapi_learning.git
```

While experimenting with some CLI clients for the server implemented in this <a href="https://github.com/behai-nguyen/fastapi_learning" title="Index of the Complete Series" target="_blank">Python FastAPI learning series</a>, I found two similar bugs in the server: both were related to Redis session entries not being cleaned up.

The first bug involves some temporary redirection entries that do not get removed after the requests are completed. The second, more significant bug, is that the logout process does not clean up the session entry if the incoming request has only the access token and no session cookies.

We address both of these bugs in this post, with most of the focus on the second one.

15. A Bug Fixed

```
git clone -b v0.15.0 https://github.com/behai-nguyen/fastapi_learning.git
```

Added the post [Python UI: A PyQt6 MDI HTTP Client Application](https://behainguyen.wordpress.com/2025/02/27/python-ui-a-pyqt6-mdi-http-client-application/) which introduces a new Python UI client.

## Implemented routes

|     | Route                      | Method | Scopes    | Response   |
| --: | -------------------------- | :----: | --------- | ---------- |
| 1   | /auth/token (/api/login)   | POST   | None      | JSON, HTML |
| 2   | /auth/login (/)            | GET    | None      | HTML       |
| 3   | /admin/me (/api/me)        | GET    | user:read | JSON, HTML |
| 4   | /auth/home                 | GET    | None      | HTML       |
| 5   | / (/auth/login)            | GET    | None      | HTML       |
| 6   | /auth/logout (/api/logout) | POST   | None      | HTML       |
| 7   | /api/me (/admin/me)        | GET    | user:read | JSON, HTML |
| 8   | /api/login (/auth/token)   | POST   | None      | JSON, HTML |
| 9   | /api/logout (/auth/logout) | POST   | None      | JSON, HTML |
| 10  | /emp/search | GET | admin:read | HTML |
| 11  | /emp/search/{partial-last-name}/{partial-first-name} | GET, POST | admin:read | HTML, JSON |
| 12  | /emp/admin-get-update/{emp_no} | GET | admin:read | HTML, JSON |
| 13  | /emp/own-get-update/{emp_no} | GET | user:read | HTML, JSON |
| 14  | /emp/admin-save | POST | admin:write | JSON |
| 15  | /emp/user-save | POST | user:write | JSON | 
| 16  | /emp/new | GET | admin:write | HTML |

## License
[MIT license](http://www.opensource.org/licenses/mit-license.php)
and the [GPL license](http://www.gnu.org/licenses/gpl.html).
