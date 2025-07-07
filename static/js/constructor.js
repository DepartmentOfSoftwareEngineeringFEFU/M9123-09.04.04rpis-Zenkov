function expandLesson(lessonNum) {
    let lessonTitle_row = document.getElementById("titl_" + lessonNum);
    let lessonContents_row = document.getElementById("cont_" + lessonNum);
    if (lessonTitle_row.getAttribute('expanded') == null ) {
        lessonContents_row.removeAttribute('hidden');
        lessonTitle_row.setAttribute('expanded','');
        lessonTitle_row.querySelector('[value="+"]').setAttribute('value','-');
    }
    else {
        lessonContents_row.setAttribute('hidden', '');
        lessonTitle_row.removeAttribute('expanded');
        lessonTitle_row.querySelector('[value="-"]').setAttribute('value','+');
    }
}

function switchLessons(lessonNum, lessonIndex_2) {
    let table = document.getElementById("lesson_table");
    let lessonTitle_row = document.getElementById("titl_" + lessonNum);
    let lessonContents_row = document.getElementById("cont_" + lessonNum);
    let lessonIndex_1 = Number(lessonTitle_row.getAttribute("index"));
    let parentNode = lessonTitle_row.parentNode;
    lessonTitle_row.setAttribute('index', String(lessonIndex_2));
    let lessonTitle2_row = document.querySelector(`.lesson_table.lesson_title[index='${lessonIndex_2}']`)
    lessonTitle2_row.setAttribute('index', String(lessonIndex_1));
    parentNode.insertBefore(lessonTitle_row, table.rows[lessonIndex_2]);
    parentNode.insertBefore(lessonContents_row, table.rows[lessonIndex_1]);

    document.querySelector(`[name="index_${lessonNum}"]`).setAttribute('value',
        lessonTitle_row.getAttribute('index'))
    document.querySelector(`[name="index_${lessonTitle2_row.getAttribute("id").substring(5)}"]`
    ).setAttribute('value', lessonTitle2_row.getAttribute('index'))
}

function moveLessonUp(lessonNum) {
    let lessonTitle_row = document.getElementById("titl_" + lessonNum);
    let lessonIndex = Number(lessonTitle_row.getAttribute("index"));
    if (lessonIndex > 1) {
        switchLessons(lessonNum, lessonIndex - 1);
    }
}

function moveLessonDown(lessonNum) {
    let lessonTitle_row = document.getElementById("titl_" + lessonNum);
    let lessonIndex = Number(lessonTitle_row.getAttribute("index"));
    let countLessons = document.getElementsByClassName("lesson_table lesson_title").length - 1;
    if (lessonIndex < countLessons) {
        let selector = `.lesson_table.lesson_title[index="${lessonIndex + 1}"]`;
        let nextLessonNum = document.querySelector(selector).getAttribute("id").substring(5);
        switchLessons(nextLessonNum, lessonIndex);
    }
}

function switchEntries(entryID, entryIndex_2) {
    let entryRow = document.getElementById(entryID);
    let entryIndex_1 = Number(entryRow.getAttribute("index"));
    let parentLessonID = entryRow.getAttribute("parent_lesson_id");
    let table = document.getElementById("tabl_" + parentLessonID);
    let parentNode = entryRow.parentNode;
    entryRow.setAttribute('index', String(entryIndex_2));
    let entryRow_2 = document.querySelector(
        `.lesson_table.lesson_entry[parent_lesson_id='${parentLessonID}'][index='${entryIndex_2}']`)
    entryRow_2.setAttribute('index', String(entryIndex_1));
    parentNode.insertBefore(entryRow, table.rows[entryIndex_2]);

    document.querySelector(`[name="index_${entryID}"]`).setAttribute('value',
        entryRow.getAttribute('index'))
    document.querySelector(`[name="index_${entryRow_2.getAttribute('id')}"]`).setAttribute(
        'value', entryRow_2.getAttribute('index'))
}

function moveEntryUp(entryID) {
    let entryRow = document.getElementById(entryID);
    let entryIndex = Number(entryRow.getAttribute("index"));
    if (entryIndex > 1) {
        switchEntries(entryID, entryIndex - 1);
    }
}

function moveEntryDown(entryID) {
    let entryRow = document.getElementById(entryID);
    let parentLessonID = entryRow.getAttribute("parent_lesson_id");
    let entryIndex = Number(entryRow.getAttribute("index"));
    let countEntries = document.querySelectorAll(
        `.lesson_table.lesson_entry[parent_lesson_id = '${parentLessonID}']`).length - 1;
    if (entryIndex < countEntries) {
        let selector = `.lesson_table.lesson_entry[parent_lesson_id=${parentLessonID}][index="${entryIndex + 1}"]`;
        let nextEntryID = document.querySelector(selector).getAttribute("id");
        switchEntries(nextEntryID, entryIndex);
    }
}