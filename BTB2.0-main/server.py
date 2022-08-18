import os
from slack_bolt import App
import logging
from slack_bolt.adapter.socket_mode import SocketModeHandler

logging.basicConfig(level=logging.DEBUG)

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
)


@app.middleware  # or app.use(log_request)
def log_request(logger, body, next):
    logger.debug(body)
    next()


@app.shortcut("new_request")
def handle_command(body, ack, client, logger, shortcut):
    logger.info(body)
    ack()

    res = client.views_open(
        trigger_id=shortcut["trigger_id"],
        view={
            "title": {"type": "plain_text", "text": "#Tech Request"},
            "submit": {"type": "plain_text", "text": "Submit"},
            "type": "modal",
            "callback_id": "request-new",
            "close": {"type": "plain_text", "text": "Cancel"},
            "blocks": [
                {
                    "block_id": "multi_block",
                    "type": "input",
                    "element": {
                        "type": "static_select", "placeholder": {"type": "plain_text", "text": "issue type"},
                        "options": [
                            {
                                "text": {"type": "plain_text", "text": "Account Issues"},
                                "value": "account-issues"
                            },
                            {
                                "text": {"type": "plain_text", "text": "M1"},
                                "value": "m1"
                            },
                            {
                                "text": {"type": "plain_text", "text": "M2"},
                                "value": "m2"
                            }
                        ],
                        "action_id": "my_action"
                    },
                    "label": {"type": "plain_text", "text": "Issue Type"}
                }
            ]
        }
    )
    logger.info(res)


@app.view("request-new")
def view_submission(ack, body, client, logger):
    ack()
    logger.info(body)
    account_issues = body["view"]["state"]["values"]["multi_block"]["my_action"]["selected_option"]["value"]
    build_new_view = {
        "type": "modal",
        "callback_id": "account-request",
        "title": {"type": "plain_text", "text": "Account Issue Request"},
        "submit": {"type": "plain_text", "text": "Submit"},
        "close": {"type": "plain_text", "text": "Cancel"},
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "This is a link to page that may help resolve your issue"},
                "accessory": {"type": "button", "text": {"type": "plain_text", "text": "Click Me"},
                              "value": "click_me_123", "url": "https://google.com", "action_id": "button-action"},
            },
            {
                "type": "input",
                "block_id": "sfid_block",
                "element": {"type": "plain_text_input", "action_id": "my_action"},
                "label": {"type": "plain_text", "text": "Salesforce Contact ID:"},

            },
            {
                "type": "input",
                "block_id": "issue_description_block",
                "element": {"type": "plain_text_input", "action_id": "my_action"},
                "label": {"type": "plain_text", "text": "Describe your issue"},
            }
        ]
    }
    build_new_view_two = {
        "type": "modal",
        "callback_id": "m1-request",
        "title": {"type": "plain_text", "text": "M1 Issue Request"},
        "submit": {"type": "plain_text", "text": "Submit"},
        "close": {"type": "plain_text", "text": "Cancel"},
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "This is a link to page that may help resolve your issue"},
                "accessory": {"type": "button", "text": {"type": "plain_text", "text": "Click Me"},
                              "value": "click_me_123", "url": "https://google.com", "action_id": "button-action"},
            },
            {
                "type": "input",
                "block_id": "sfid_block",
                "element": {"type": "plain_text_input", "action_id": "my_action"},
                "label": {"type": "plain_text", "text": "Project ID:"},

            },
            {
                "type": "input",
                "block_id": "issue_description_block",
                "element": {"type": "plain_text_input", "action_id": "my_action"},
                "label": {"type": "plain_text", "text": "Describe your issue"},
            }
        ]
    }
    build_new_view_three = {
        "type": "modal",
        "callback_id": "m2-request",
        "title": {"type": "plain_text", "text": "M2 Issue Request"},
        "submit": {"type": "plain_text", "text": "Submit"},
        "close": {"type": "plain_text", "text": "Cancel"},
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "This is a link to page that may help resolve your issue"},
                "accessory": {"type": "button", "text": {"type": "plain_text", "text": "Click Me"},
                              "value": "click_me_123", "url": "https://google.com", "action_id": "button-action"},
            },
            {
                "type": "input",
                "block_id": "sfid_block",
                "element": {"type": "plain_text_input", "action_id": "my_action"},
                "label": {"type": "plain_text", "text": "Project ID:"},

            },
            {
                "type": "input",
                "block_id": "issue_description_block",
                "element": {"type": "plain_text_input", "action_id": "my_action"},
                "label": {"type": "plain_text", "text": "Describe your issue"},
            }
        ]
    }
    if account_issues == "account-issues":
        ack(response_action="update", view=build_new_view)
    elif account_issues == "m1":
        ack(response_action="update", view=build_new_view_two)
    elif account_issues == "m2":
        ack(response_action="update", view=build_new_view_three)


# Step 4: The path that allows for your server to receive information from the modal sent in Slack
@app.view("account-request")
def view_submission(ack, body, client, logger):
    ack()
    logger.info(body["view"]["state"]["values"])
    tech_channel = "C035D0W53QE"
    user_text = body["view"]["state"]["values"]["sfid_block"]["my_action"]["value"]
    issue_description_text = body["view"]["state"]["values"]["issue_description_block"]["my_action"]["value"]
    user_id = body["user"]["username"]
    ack()
    client.chat_postMessage(channel=tech_channel, blocks=[
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"<@{user_id}>" + " " + "Created an Account Issues Request!",
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Salesforce Contact ID:\n*<google.com|{user_text}>*\nIssue Description:\n{issue_description_text}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": f"<@{user_id}>" + " " + "will begin working on your issue shortly\n"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": "Please add pictures and screenshots that will help us identify your issue."
            }
        }

    ]
    )

#    client.chat_postMessage(channel=tech_channel, text=(
#           f"*Tech request opened by:* <@{user_id}>!" + "\n" + "*Salesforce ContactID/Link:*" + " " + user_text + "\n" + "*Issue Description:*" + " " + issue_description_text))


@app.view("m1-request")
def view_submission(ack, body, client, logger):
    ack()
    logger.info(body["view"]["state"]["values"])
    tech_channel = "C035D0W53QE"
    user_text = body["view"]["state"]["values"]["sfid_block"]["my_action"]["value"]
    issue_description_text = body["view"]["state"]["values"]["issue_description_block"]["my_action"]["value"]
    user_id = body["user"]["username"]
    ack()
    client.chat_postMessage(channel=tech_channel, blocks=[
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"<@{user_id}>" + " " + "Created an M1 Issues Request!",
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Project ID:\n*<google.com|{user_text}>*\nIssue Description:\n{issue_description_text}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": f"<@{user_id}>" + " " + "will begin working on your issue shortly"
            }
        }

    ]
                            )


@app.view("m2-request")
def view_submission(ack, body, client, logger):
    ack()
    logger.info(body["view"]["state"]["values"])
    tech_channel = "C035D0W53QE"
    user_text = body["view"]["state"]["values"]["sfid_block"]["my_action"]["value"]
    issue_description_text = body["view"]["state"]["values"]["issue_description_block"]["my_action"]["value"]
    user_id = body["user"]["username"]
    ack()
    client.chat_postMessage(channel=tech_channel, blocks=[
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"<@{user_id}>" + " " + "Created an M1 Issues Request!",
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Project ID:\n*<google.com|{user_text}>*\nIssue Description:\n{issue_description_text}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": f"<@{user_id}>" + " " + "will begin working on your issue shortly"
            }
        }

    ]
                            )


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
