import frappe
import paramiko
import io


def fetch_messages():
    frappe.enqueue(exec, queue="long")


# def enqueue_long_job(arg1, args2):
#     frappe.enqueue('myapp.mymodule.long_job', arg1=arg1, arg2=arg2)


def exec():
    docs = frappe.get_all(
        "EDI Connection",
        fields=["host", "username", "private_key", "customer", "name"],
        filters={"is_incomming": True},
    )
    for doc in docs:
        str_key = io.StringIO(doc.private_key)
        mykey = paramiko.RSAKey.from_private_key(str_key)
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.load_system_host_keys()
        ssh_client.connect(
            hostname=doc.host,
            username=doc.username,
            allow_agent=True,
            pkey=mykey,
        )

        ftp_client = ssh_client.open_sftp()
        root_file = "/download"
        files = ftp_client.listdir("/download")
        for file in files:
            # existing = frappe.db.exists("EDI Log", file)
            # if existing:
            #     continue
            remote_file = f"{root_file}/{file}"
            # local_file = f"/tmp/file"
            with ftp_client.open(remote_file, "r") as f:
                line = f.readline()
                existing = frappe.db.exists("EDI Log", file)
                if existing:
                    edi_log_doc = frappe.get_doc("EDI Log", file)
                    if edi_log_doc.content != line:
                        print(edi_log_doc.content)
                        print("==============")
                        print(line)
                        print("==============")
                    print("already exists: " + file)
                    f.close()
                    continue
                edi_log = frappe.new_doc("EDI Log")
                edi_log.file_name = file
                edi_log.content = line
                edi_log.customer = doc.customer
                edi_log.edi_connection = doc.name
                edi_log.save()
                frappe.db.commit()
                f.close()
                ftp_client.remove(remote_file)
        ftp_client.close()
        ssh_client.close()
