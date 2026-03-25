function createAffiliationSurveyForm() {
    // 1. Create the Form
    var form = FormApp.create('東京科学大学 系所属調査アンケート 25B');

    form.setDescription('このアンケートは、2025年度（25B）の系所属結果を調査し、ボーダー点を推定するためのものです。\n' +
        '収集したデータは統計的に処理され、個人が特定される形では公開されません。\n' +
        '※回答の重複を防ぐためGoogleアカウントへのログインが必要ですが、メールアドレスは収集されません。\n' +
        'ご協力をお願いいたします。 \n' +
        '\n' +
        '※注意　入学時点で既に系が決まっている総合型一般枠などは回答する必要ありません。'
                       )
        .setLimitOneResponsePerUser(true);

    // 2. Define Options

    // List of Schools (学院)
    var schools = [
        '理学院',
        '工学院',
        '物質理工学院',
        '情報理工学院',
        '生命理工学院',
        '環境・社会理工学院'
    ];

    // List of Departments (系) - Based on Science Tokyo / Tokyo Tech structure
    var departments = [
        '数学系',
        '物理学系',
        '化学系',
        '地球惑星科学系',
        '機械系',
        'システム制御系',
        '電気電子系',
        '情報通信系',
        '経営工学系',
        '材料系',
        '応用化学系',
        '数理・計算科学系',
        '情報工学系',
        '生命理工学系',
        '建築学系',
        '土木・環境工学系',
        '融合理工学系'
    ];

    // 3. Add Questions

    // Q1. Score (系所属点)
    form.addTextItem()
        .setTitle('系所属点（3100点満点）')
        .setHelpText('整数で入力してください。正確な点数が不明な場合は回答を控えてください。')
        .setRequired(true);

    // Q2. Affiliated School (Before)
    form.addListItem()
        .setTitle('所属学院（1年次）')
        .setChoiceValues(schools)
        .setRequired(true);

    // Q3-Q8. Desired Departments (1st to 6th choice)
    form.addSectionHeaderItem()
        .setTitle('志望する系について')
        .setHelpText('自身が提出した志望順位通りに記入してください。');

    for (var i = 1; i <= 6; i++) {
        var item = form.addListItem();
        item.setTitle('第' + i + '志望');
        // Only 1st choice is required
        item.setRequired(i === 1);
        item.setChoiceValues(departments);
    }

    // Q9. Final Result
    form.addSectionHeaderItem().setTitle('系所属結果');

    var finalResultOptions = departments.slice(); // Copy array
    finalResultOptions.push('系所属不可');

    form.addListItem()
        .setTitle('実際に所属が決定した系')
        .setHelpText('もし系所属できずに留年が決まった場合は「系所属不可」を選択してください。')
        .setChoiceValues(finalResultOptions)
        .setRequired(true);

    // Q10. Voluntary Repetition
    form.addSectionHeaderItem().setTitle('留年・進路選択について');

    form.addMultipleChoiceItem()
        .setTitle('希望留年の有無')
        .setHelpText('志望する系に行くために、あえて留年（または所属辞退）を選択しましたか？')
        .setChoiceValues(['はい', 'いいえ'])
        .setRequired(true);

    // Q11-Q13. Comments
    form.addSectionHeaderItem().setTitle('コメント・感想');

    form.addParagraphTextItem()
        .setTitle('感想・アドバイス')
        .setHelpText('大学生活(講義・サークル・バイト・一人暮らしなど)に関する感想や反省、理工学系の後輩へのメッセージ・アドバイスなど');

    form.addParagraphTextItem()
        .setTitle('自由回答欄')
        .setHelpText('その他、ご自由にお書きください。');

    // 4. Log the URL
    Logger.log('Form ID: ' + form.getId());
    Logger.log('Edit URL: ' + form.getEditUrl());
    Logger.log('Published URL: ' + form.getPublishedUrl());
}
