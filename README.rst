===============================
Downloader amazon cloud drive
===============================

Images downloader for folder in Amazon cloud
Uses asycio so tested python >= 3.4

.. code-block:: bash

    pip install --upgrade git+git://github.com/PythonicNinja/downloader-amazon-cloud-drive.git

usage:

.. code-block:: bash

    python3 downloader.py https://www.amazon.com/clouddrive/share/7FDg46D18TepcOoyS7HPuU9oVCvNhBMuFDvu2fRA6qR/folder/EnUiZP-JR5KGXJ3FGvDPUw

or:

.. code-block:: bash

   >>> from amazon_downloader import downloader
   >>> downloader.AmazonDownloader(share_link='https://www.amazon.com/clouddrive/share/7FDg46D18TepcOoyS7HPuU9oVCvNhBMuFDvu2fRA6qR/folder/EnUiZP-JR5KGXJ3FGvDPUw')

* Free software: BSD license
