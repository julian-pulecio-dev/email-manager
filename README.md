# Email Manager

## 🎯About

Email Manager is a cloud-based, AI-powered solution designed to automate the analysis, creation, organization, and classification of emails in Gmail based on their content and attachments. It enables a highly personalized and customizable experience within your Gmail inbox by leveraging the full potential of artificial intelligence.

### email creation feature
This feature takes a list of attachments and a general description from the user, then extracts or completes the following information: recipient email address, subject, title, and body. If the provided information is not sufficient, the system will notify the user that further clarification is needed. Once the system fully understands the instructions, it will successfully send the email to the specified recipient.

### email clasification feature
With this feature, you can create custom labels for your emails and associate them with specific filtering rules. When an incoming email matches these instructions, it will automatically be classified under the corresponding custom label.  


## ✅ Requirements

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```# Clone this project
$ git clone https://github.com/julian-pulecio-dev/email-manager

# Access
$ cd email-manager

# Install dependencies
$ brew install hashicorp/tap/terraform

# deploy project
$ terraform init

$ terraform plan

$ terraform apply
```
## Architecture
<img width="1365" height="899" alt="Captura de pantalla 2025-11-10 102331" src="https://github.com/user-attachments/assets/a3b0a933-700f-42f1-932c-916bb4ad0412" />

## Auth flow
<img width="798" height="490" alt="auth flow email manager " src="https://github.com/user-attachments/assets/808a8572-bdf3-4592-b5b8-3292d16e3ffc" />

## Contributing

Pull requests are welcome.
 For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License


[MIT](https://choosealicense.com/licenses/mit/)
