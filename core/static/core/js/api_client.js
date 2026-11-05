async function showAssignments() {
  const list = document.querySelector("#api-assignment-list");
  const statusLine = document.querySelector("#api-status");
  const url = "/api/assignments/?format=json";

  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const page = await response.json();

    for (const assignment of page.results) {
      const item = document.createElement("li");
      item.textContent = assignment.title;
      list.append(item);
    }
    statusLine.textContent = `Assignments on this page: ${page.results.length}`;
  } catch (error) {
    statusLine.textContent = `Could not load assignments: ${error.message}`;
  }
}

showAssignments();
