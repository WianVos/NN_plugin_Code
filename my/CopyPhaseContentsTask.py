import sys

setToken_method = task.getClass().getMethod('set$token', String)
def strip_task(task):
  setToken_method.invoke(task._delegate, None)
  task.id = None
  if task.type == 'xlrelease.ParallelGroup':
    task.tasks = []

def copy_tasks(tasks, target_container_id):
  for task in tasks:
    subtasks = None
    if task.type == 'xlrelease.ParallelGroup':
      subtasks = task.tasks
    strip_task(task)
    new_task_id = taskApi.addTask(target_container_id, task).id
    if subtasks is not None:
      copy_tasks(subtasks, new_task_id)

source_template_id = None
if sourceTemplateTitle is not None:
  # assuming only one
  source_template_id = getReleasesByTitle(sourceTemplateTitle)[0].id

# assuming only one
source_phase = getPhasesByTitle(sourcePhaseTitle, source_template_id)[0]
this_phase = getCurrentPhase()
copy_tasks(source_phase.tasks, getCurrentPhase().id)

# TODO: use https://docs.xebialabs.com/xl-release/4.0.x/rest-api/com.xebialabs.xlrelease.api.internal.ReleaseResource.html#/releases/{releaseId}/tasks/move:POST to move the tasks to the right place in the phase