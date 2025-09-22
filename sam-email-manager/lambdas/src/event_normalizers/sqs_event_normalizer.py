from logging import getLogger
from typing import Any
from src.models.events.sqs_queue_event import SQSQueueEvent
from src.event_normalizers.base_event_normalizer import BaseEventHandler
from src.decorators.log_function_call import log_function_call

logger = getLogger(__name__)

class SqsEventNormalizer(BaseEventHandler):
    
    @log_function_call
    def handle(self, event: dict, context: dict, **kwargs: Any) -> dict:
        failure_responses = []

        for record in event['Records']:
            lambda_event = SQSQueueEvent.from_sqs_record(record)
            try:
                if self.request_class is None:
                    _ = self.func(lambda_event, context, **kwargs)
                    continue
                request = self.request_class.from_event(lambda_event)
                _ = self.func(request, context, **kwargs)
            except Exception as e:
                logger.error(f"Error processing record {record['messageId']}: {str(e)}")
                if logger.level == 10:  # DEBUG level
                    raise e  # Re-raise the error in debug mode for visibility
                failure_responses.append({"itemIdentifier": record["messageId"]})

        if failure_responses:
            return {"batchItemFailures": failure_responses}
