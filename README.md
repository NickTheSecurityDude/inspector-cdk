# inspector-cdk

## Parse Inspector Results Using CDK

Howto Install:  
If needed, export your AWS profile:  
`export AWS_PROFILE=profile_name`

Create a virtual environment and launch the stacks:  
```
python3 -m venv .venv  
source .venv/bin/activate   
python3 -m pip install -r requirements.txt  
cdk bootstrap aws://<account-id>/<region>  
cdk synth   
cdk deploy --all
```

Inspector will run daily, or you can run it on demand.

(c) Copyright 2020 - NickTheSecurityDude

Disclaimer:  
For informational/educational purposes only.  Bugs are likely and can be reported on github.  
Using this will incur AWS charges.
