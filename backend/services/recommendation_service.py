from decimal import Decimal

PRODUCTS = {
 "home": [
  {"category":"Lighting","item":"LED Bulb (Warm White)","description":"Energy-efficient LED bulbs for general lighting.","price":100,"quantity":5,"platforms":["Amazon","Flipkart","IKEA"]},
  {"category":"Ceiling Fans","item":"Havells Ceiling Fan","description":"Basic, functional ceiling fan for everyday use.","price":2500,"quantity":2,"platforms":["Amazon","Flipkart","Myntra"]},
  {"category":"Furniture","item":"Plastic Chair","description":"Stackable plastic chair for kitchen or living room.","price":1250,"quantity":2,"platforms":["Amazon","Flipkart","IKEA"]},
  {"category":"Furniture","item":"Small Wooden Table","description":"Simple wooden table for dining or side use.","price":3500,"quantity":1,"platforms":["Amazon","IKEA","AJIO"]},
 ],
 "party": [
  {"category":"Venue","item":"Home setup","description":"Use the home space for the event and save venue cost.","price":0,"platforms":["OYO"]},
  {"category":"Catering","item":"Home-cooked meal","description":"Simple menu for the requested guest count.","price":2500,"platforms":["Swiggy","Zomato"]},
  {"category":"Entertainment","item":"Streaming movie subscription","description":"Low-cost entertainment for a relaxed gathering.","price":500,"platforms":["Amazon","Flipkart"]},
  {"category":"Decoration","item":"DIY balloon decoration kit","description":"Budget-friendly party decoration set.","price":1200,"platforms":["Amazon","Flipkart"]},
 ],
 "jewelry": [
  {"item":"Minimal bracelet","description":"A simple bracelet that complements both traditional and casual outfits.","price":1800,"style":"Casual","platforms":["Amazon","Flipkart","Myntra"]},
  {"item":"Elegant ring","description":"A delicate ring suitable for a birthday, dinner or celebration.","price":2200,"style":"Elegant","platforms":["Amazon","Flipkart","AJIO"]},
  {"item":"Classic pendant","description":"A clean pendant for a polished occasion look.","price":3200,"style":"Classic","platforms":["Amazon","Flipkart","Myntra"]},
 ]
}

def _scale(items, budget):
    budget = float(budget or 0)
    if not items: return items, 0
    total = sum(float(x["price"]) * float(x.get("quantity",1)) for x in items)
    if total <= budget or budget <= 0: return items, total
    factor = budget / total
    out=[]; running=0
    for x in items:
        y=dict(x); y["quantity"] = max(1, int(float(y.get("quantity",1))*factor)); running += float(y["price"])*y["quantity"]; out.append(y)
    return out, running

def home_fallback(data):
    items, spent = _scale(PRODUCTS["home"], data.get("budget"))
    rooms = data.get("rooms") or []
    return {"title":"Your Personalized Budget Plan","total_budget":float(data.get("budget",0)),"allocated":round(spent,2),"remaining":round(max(0,float(data.get("budget",0))-spent),2),"groups":items,"rooms":rooms,"additional_suggestions":["Consider purchasing used furniture for further cost savings.","Look for sales and discounts on online marketplaces.","Prioritize essential items and postpone non-essential purchases."]}

def party_fallback(data):
    budget=float(data.get("budget",0)); guests=max(1,int(data.get("guests",1)))
    venue=0 if data.get("venue","Home")=="Home" else round(budget*.12,2)
    catering=round(budget*.40,2); decor=round(budget*.18,2); entertainment=round(budget*.20,2); contingency=round(budget-venue-catering-decor-entertainment,2)
    groups=[{"category":"Venue","item":data.get("venue","Home"),"description":"Venue plan matched to your event.","price":venue,"platforms":["OYO"]},{"category":"Catering","item":"Party catering","description":f"Food plan for approximately {guests} guests.","price":catering,"platforms":["Swiggy","Zomato"]},{"category":"Decoration","item":"Theme decoration","description":"Decor package matched to the event type.","price":decor,"platforms":["Amazon","Flipkart"]},{"category":"Entertainment","item":"Entertainment package","description":"Music and activity options for the event.","price":entertainment,"platforms":["Amazon","Flipkart"]},{"category":"Contingency","item":"Unexpected expenses","description":"Reserve for last-minute needs.","price":max(0,contingency),"platforms":["Amazon"]}]
    return {"title":"Your Party Budget Plan","budget":budget,"allocated":round(sum(x['price'] for x in groups),2),"remaining":round(max(0,budget-sum(x['price'] for x in groups)),2),"groups":groups,"venue_suggestions":["Home","Local banquet hall","Restaurant/private dining","Community hall"],"additional_suggestions":["Confirm catering quantities with your guest count.","Compare venue quotes before paying a deposit.","DIY decorations can reduce costs for smaller events."]}

def jewelry_fallback(data):
    budget=float(data.get("budget",0)); items=[]
    for x in PRODUCTS["jewelry"]:
        if x["price"] <= budget or budget <= 0: items.append(x)
    if not items: items=PRODUCTS["jewelry"][:2]
    spent=sum(x["price"] for x in items)
    return {"title":"Your Personalized Jewelry Recommendations","total_budget":budget,"remaining":round(max(0,budget-spent),2),"outfit_analysis":{"color":"Color coordination based on your inputs","style":data.get("style","Elegant"),"formality":"Occasion appropriate"},"items":items,"styling_tips":["Keep the jewelry metal consistent with the main accents of the outfit.","Choose one statement piece and keep the remaining pieces balanced.","Match the scale of the jewelry to the outfit neckline and occasion."]}
