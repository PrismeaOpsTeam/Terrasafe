# Terrasafe

https://github.com/PrismeaOpsTeam/Terrasafe

Terrasafe provide a way to secure your automated terraform pipeline and fail if an unauthorized deletion is planned.

## Usage

```sh
terraform plan -out=tfplan
terraform show -json tfplan | terrasafe --config terrasafe.json
terraform apply --auto-approve tfplan
```

## Configuration

The `--config` option allows to specify the path of the JSON configuration file.

```json
{
  "ignore_deletion": [ "aws_ecs_task_definition*" ], // Resource can be deleted
  "ignore_deletion_if_recreation": [ "aws_ecs_task_definition*"], // Resource can be replaced
  "unauthorized_deletion": [ "aws_ecs_task_definition*" ] // Resource can't be deleted by any way
}
```

## How to delete a resource ?

* Comment it
* Or rename the file with the extension `.tf.disabled`
* Or define the Env var `TERRASAFE_ALLOW_DELETION` to the addresses of resources to delete, separated by `;`.
Example: `export TERRASAFE_ALLOW_DELETION=aws_ecs_task_definition.a;aws_lambda.b`



