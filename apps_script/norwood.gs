/**
 * Norwood lead capture — Google Apps Script Web App.
 *
 * Deployed as: Web app, "Execute as: Me", "Who has access: Anyone".
 * Receives JSON from https://start.grafto.hair/ Norwood form, appends a row
 * to the spreadsheet "Collected emails: Norwood scale", and emails the user
 * a confirmation with their estimate.
 *
 * No API keys are stored client-side. The Apps Script runs as the spreadsheet
 * owner and uses MailApp to send via the owner's Gmail quota.
 */

var SHEET_ID = '1CyK6Ru-olLOl47ljWN1oSdNb42W1UwM9wDonER8jXtM';
var SHEET_NAME = 'Sheet1';
var ALLOWED_ORIGIN = 'https://start.grafto.hair';
var APP_URL = 'https://apps.apple.com/app/grafto-hair-transplant-smp/id6759666757';

function doOptions(e) {
  return _cors(ContentService.createTextOutput(''));
}

function doPost(e) {
  try {
    var body = JSON.parse(e.postData.contents || '{}');

    var email      = String(body.email      || '').trim();
    var stage      = String(body.stage      || '');
    var language   = (body.language === 'ru') ? 'ru' : 'en';
    var pattern    = String(body.pattern    || '');
    var grafts     = String(body.grafts     || '');
    var nextStep   = String(body.nextStep   || '');
    var source     = String(body.source     || 'landing-norwood');
    var pageUrl    = String(body.pageUrl    || '');
    var referrer   = String(body.referrer   || '');
    var userAgent  = String(body.userAgent  || '');
    var timestamp  = body.timestamp ? new Date(body.timestamp) : new Date();

    if (!_isValidEmail(email)) {
      return _json({ ok: false, error: 'invalid_email' }, 400);
    }
    if (!stage) {
      return _json({ ok: false, error: 'missing_stage' }, 400);
    }

    // 1. Append row to the sheet.
    var ss = SpreadsheetApp.openById(SHEET_ID);
    var sheet = ss.getSheetByName(SHEET_NAME);
    if (!sheet) {
      sheet = ss.insertSheet(SHEET_NAME);
      sheet.appendRow([
        'Timestamp','Email','Language','Norwood Stage','Pattern',
        'Graft Estimate','Best Next Step','Source','Page URL','Referrer','User Agent'
      ]);
    }
    sheet.appendRow([
      timestamp, email, language, stage, pattern,
      grafts, nextStep, source, pageUrl, referrer, userAgent
    ]);

    // 2. Send confirmation email.
    _sendConfirmation(email, language, stage, pattern, grafts, nextStep);

    return _json({ ok: true });
  } catch (err) {
    return _json({ ok: false, error: String(err && err.message || err) }, 500);
  }
}

function _sendConfirmation(email, language, stage, pattern, grafts, nextStep) {
  var copy = (language === 'ru') ? {
    subject: 'Ваш расчёт Grafto: Норвуд ' + stage,
    title: 'Ваш расчёт по шкале Норвуда',
    stageLabel: 'Стадия',
    patternLabel: 'Паттерн',
    graftsLabel: 'Ориентир по графтам',
    nextLabel: 'Лучший следующий шаг',
    cta: 'Получите детальный разбор по фото — стоимость пересадки и SMP в разных странах и персональные рекомендации — в приложении Grafto.',
    button: 'Открыть в App Store',
    disclaimer: 'Это не медицинская рекомендация. Окончательный план зависит от оценки донорской зоны и заключения хирурга.'
  } : {
    subject: 'Your Grafto estimate: Norwood ' + stage,
    title: 'Your Norwood estimate',
    stageLabel: 'Stage',
    patternLabel: 'Pattern',
    graftsLabel: 'Graft estimate',
    nextLabel: 'Best next step',
    cta: 'Get a detailed photo-based breakdown — costs in different countries for hair transplant and SMP, and personalized recommendations — in the Grafto app.',
    button: 'Open in the App Store',
    disclaimer: 'Not medical advice. Final planning depends on donor assessment and surgeon evaluation.'
  };

  var html =
    '<div style="font-family:Helvetica,Arial,sans-serif;max-width:560px;margin:0 auto;color:#0f172a">' +
      '<h1 style="font-size:22px;margin:0 0 16px">' + copy.title + '</h1>' +
      '<p style="margin:0 0 8px"><strong>' + copy.stageLabel + ':</strong> Norwood ' + stage + '</p>' +
      '<p style="margin:0 0 8px"><strong>' + copy.patternLabel + ':</strong> ' + _escape(pattern) + '</p>' +
      '<p style="margin:0 0 8px"><strong>' + copy.graftsLabel + ':</strong> ' + _escape(grafts) + '</p>' +
      '<p style="margin:0 0 24px"><strong>' + copy.nextLabel + ':</strong> ' + _escape(nextStep) + '</p>' +
      '<div style="background:#E8F4FA;border-left:4px solid #0B6E99;border-radius:12px;padding:20px;margin:0 0 24px">' +
        '<p style="margin:0 0 16px;font-size:16px;line-height:1.5;font-weight:600">' + copy.cta + '</p>' +
        '<a href="' + APP_URL + '" style="display:inline-block;background:#0B6E99;color:#fff;text-decoration:none;padding:12px 20px;border-radius:8px;font-weight:600">' + copy.button + '</a>' +
      '</div>' +
      '<p style="font-size:12px;color:#64748b;font-style:italic;margin:0">' + copy.disclaimer + '</p>' +
    '</div>';

  MailApp.sendEmail({
    to: email,
    subject: copy.subject,
    htmlBody: html,
    name: 'Grafto'
  });
}

function _isValidEmail(s) { return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(s); }
function _escape(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function _json(obj, status) {
  return _cors(ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON));
}
function _cors(out) {
  // Apps Script Web Apps return permissive CORS by default for "Anyone" access.
  // Headers cannot be customised on the response object; fetch() from the
  // browser still works because Apps Script serves with appropriate CORS.
  return out;
}
