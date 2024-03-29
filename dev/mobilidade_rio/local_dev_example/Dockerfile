FROM python:3.8-slim

# install postgresql-client
RUN apt-get update && apt-get install -y postgresql-client

# Install virtualenv and create a virtual environment
RUN pip install --no-cache-dir virtualenv==20.6.0 && virtualenv /env --python=python3.8
ENV PATH /env/bin:$PATH

# Install pip requirements
WORKDIR /app
COPY requirements.txt .
RUN /env/bin/pip install --no-cache-dir -r requirements.txt

# Install nginx and copy configuration
RUN apt-get update && apt-get install -y --no-install-recommends nginx \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
COPY /mobilidade_rio_nginx.conf /etc/nginx/sites-available/default

# Copy app, generate static and set permissions
COPY . .
RUN /env/bin/python manage.py collectstatic --no-input --settings=mobilidade_rio.settings.base && \
  chown -R www-data:www-data /app

# Expose
EXPOSE 80
STOPSIGNAL SIGTERM

# Run commands 
CMD ["/bin/bash", "-c", "'python manage.py runserver'"]