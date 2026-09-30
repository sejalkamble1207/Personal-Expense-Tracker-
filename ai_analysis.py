from collections import defaultdict


def analyze_expenses(expenses, month):
    """
    Transparent rule-based spending analysis.
    This is intentionally not presented as a generative AI model.
    It analyzes the user's actual expense records.
    """
    total = sum(float(e["amount"]) for e in expenses)
    count = len(expenses)
    highest = max(expenses, key=lambda e: float(e["amount"])) if expenses else None

    by_category = defaultdict(float)
    for expense in expenses:
        by_category[expense["category"]] += float(expense["amount"])

    category_totals = sorted(
        by_category.items(),
        key=lambda item: item[1],
        reverse=True
    )

    top_category = category_totals[0][0] if category_totals else "No data"
    top_amount = category_totals[0][1] if category_totals else 0
    top_percentage = (top_amount / total * 100) if total else 0

    insights = []
    recommendations = []

    if not expenses:
        insights.append("There are no expenses recorded for this month yet.")
        recommendations.append("Add a few expenses to unlock personalized spending insights.")
    else:
        insights.append(
            f"You recorded {count} expense{'s' if count != 1 else ''} "
            f"totalling ₹{total:,.2f} in {month}."
        )
        insights.append(
            f"{top_category} is your highest spending category at "
            f"₹{top_amount:,.2f} ({top_percentage:.1f}% of your recorded spending)."
        )

        if highest:
            insights.append(
                f"Your highest single expense is "
                f"₹{float(highest['amount']):,.2f} for {highest['description']}."
            )

        if top_percentage >= 50:
            recommendations.append(
                f"{top_category} represents more than half of your recorded spending. "
                "Review the individual transactions in this category to understand the pattern."
            )
        elif top_percentage >= 30:
            recommendations.append(
                f"{top_category} is a major spending category. "
                "Review recurring purchases in this category."
            )
        else:
            recommendations.append(
                "Your recorded spending is spread across several categories. "
                "Continue tracking expenses to build a clearer monthly pattern."
            )

        if count < 5:
            recommendations.append(
                "Keep recording expenses consistently; more data can make the analysis more useful."
            )

    category_data = [
        {
            "category": category,
            "amount": round(amount, 2),
            "percentage": round((amount / total * 100), 1) if total else 0
        }
        for category, amount in category_totals
    ]

    return {
        "month": month,
        "total": round(total, 2),
        "count": count,
        "highest": round(float(highest["amount"]), 2) if highest else 0,
        "highest_description": highest["description"] if highest else "—",
        "top_category": top_category,
        "top_percentage": round(top_percentage, 1),
        "category_data": category_data,
        "insights": insights,
        "recommendations": recommendations
    }
